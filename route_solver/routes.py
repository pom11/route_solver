from pyroutelib3 import Router, Datastore
import os
# print("Loading romania-latest.osm.pbf...")
# workdir = os.getcwd()
# router = Router("car",f"{workdir}/romania-latest.osm.pbf","pbf")
# print("Loaded")
router = Router("car")

from sanic import Sanic
from sanic.response import json, file, html, text, redirect
from sanic.exceptions import abort
from sanic_cors import CORS, cross_origin

import async_solver

import pandas as pd
import numpy as np
import requests
import json as jjson


#####SANIC APP CONFIGS#####
app = Sanic(__name__,load_env=False)
CORS(app,automatic_options=True,supports_credentials=True)
app.config.KEEP_ALIVE = True

####ALL ERRORS#####
async def server_error_handler(request, exception):
	return text("Error or you try too much, limit 60/minute", status=500)

app.error_handler.add(Exception, server_error_handler)

#####LIVE HEALTH CHECK#####
@app.route("/",methods=["GET"])
async def live(request):
	ret = "live"
	return(text(ret,headers={'X-Served-By':'routes.app','Content-Length':len(ret.encode('utf-8'))},status=200))


@app.route("/dm/",methods=["POST"])
async def live(request):
	points = request.json['points']
	ret = await get_dm([tuple(x) for x in points])
	return(json(ret,headers={'X-Served-By':'routes.app'},status=200))


@app.route("/solve",methods=["POST"])
async def solver(request):
	dm = await get_dm([tuple(x) for x in request.json['points']])
	data = {
	"weights":dm['dm'],
	"service_times":request.json['service_times'],
	"demands":request.json['demands'],
	"time_windows":request.json['time_windows'],
	"vehicle_capacities":request.json['vehicle_capacities'],
	"depot":request.json['depot'],
	'num_locations': len(request.json['time_windows']),
	'num_vehicles': len(request.json['vehicle_capacities'])
	}
	solver = await async_solver.solve(data)
	resp = await final_resp(dm,solver)
	return(json(resp,headers={'X-Served-By':'routes.app'},status=200))

async def final_resp(dm,rutes):
	for k,vehicle in enumerate(rutes['solver']):	
		route = vehicle['route']
		nodes = []
		if len(route)>2:
			for i,node in enumerate(route):
				if i>0:
					r = dm['routes'][f'{route[i-1]["node"]}|{node["node"]}']
					for j in r:
						nodes.append(j)
		rutes['solver'][k]['node_rute'] = nodes
	return rutes



async def get_dm(list_dm):
	df = pd.DataFrame([[np.nan]*len(list_dm)]*len(list_dm),index=list_dm,columns=list_dm)
	r = {}
	for i in range(len(list_dm)):
		for j in range(len(list_dm)):
			if j>i:
				rr = await get_route(list_dm[i],list_dm[j])
				df.iloc[i,j] = rr[0]
				r[f'{i}|{j}'] = rr[1]
				r[f'{j}|{i}'] = rr[1]
				df.iloc[j,i] = df.iloc[i,j]
	for i in range(len(list_dm)):
		df.iloc[i,i] = 0
		r[f'{i}|{i}'] = []

	return({'dm':df.to_numpy().tolist(),'routes':r})

async def get_route(point1, point2):
	start = router.findNode(point1[0],point1[1])
	end = router.findNode(point2[0],point2[1])
	status, route = router.doRoute(start,end)

	if status == 'success':
		routeLatLons = list(map(router.nodeLatLon,route))
		dist = 0

		for crt,latlng in enumerate(routeLatLons):
			if crt >=1:
				dist = dist + Datastore.distance(routeLatLons[crt-1],routeLatLons[crt])
		return([dist,routeLatLons])
	else:
		return([])


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8001,debug=True)#,ssl=context)

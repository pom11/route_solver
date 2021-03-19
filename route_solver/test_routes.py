from pyroutelib3 import Router, Datastore
import pandas as pd
import numpy as np
import os

workdir = os.getcwd()
print("Loading romania-latest.osm.pbf")
router = Router("car",f"{workdir}/romania-latest.osm.pbf","pbf")
print('Done')

def get_route(point1, point2):
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

point1 = (44.2913,28.5628)
point2 = (44.2576,28.5586)


def get_dm(list_dm):
	df = pd.DataFrame([[np.nan]*len(list_dm)]*len(list_dm),index=list_dm,columns=list_dm)
	for i in range(len(list_dm)):
		for j in range(len(list_dm)):
			if j>i:
				df.iloc[i,j] = get_route(list_dm[i],list_dm[j])[0]
				df.iloc[j,i] = df.iloc[i,j]
	for i in range(len(list_dm)):
		df.iloc[i,i] = 0

	return(df.to_numpy())

# print(get_route(point1,point2))

get_dm([(44.2843769, 28.5568986), (44.2843384, 28.556908), (44.284097, 28.5568624), (44.2837467, 28.556861)])
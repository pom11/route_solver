# route_solver
 Server optimizare rute - Capacitated Vehicle Routing Problem with Time Windows (CVRPTW)

#DOCKER
docker-compose -f docker-compose.yaml build
docker-compose -f docker-compose.yaml up

#test_routes.py
## get_route(point1, point2)
- returneaza distanta dintre point1 si point2 si traseul de urmat
- [float(distanta),lista_traseu]

#solver.py
- python solver.py data.sample.yaml

#async_solver.py
- Varianta async a solver.py

#routes.py
- server async python

#solve

##service_times
- timp de stationare

##demands
- incarcare per punct geografic

##vehcile_capacities
- capacitate incarcare auto
- numarul de auto se initializeaza prin introducerea unei noi capacitati

##points
- coordonate puncte de atins

##depot
- index punct de plecare din lista points. 

```curl --silent --location --request POST 'http://192.168.236.211:8001/solve' \
--header 'Content-Type: application/json' \
--data-raw '{
    "depot": 0,
    "service_times": [
        0,
        5,
        5
    ],
    "time_windows": [
        [
            0,
            0
        ],
        [
            0,
            5400
        ],
        [
            0,
            5400
        ]
    ],
    "demands": [
        0,
        1,
        1
    ],
    "vehicle_capacities": [
        20
    ],
    "points": [
        [
            44.301738,
            28.581618
        ],
        [
            44.161693871305886,
            28.629600967397156
        ],
        [
            44.18059206612445,
            28.64456970186457
        ]
    ]
}'```

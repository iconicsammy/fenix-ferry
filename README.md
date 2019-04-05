# Fenix Intl Part 1: Ferry

While the code runs on python 2 and 3, tests won't work on python 2.

# Running the app

from command prompt type:

    python app.py

where you will see tips.

NOTE: when entering strings, please use '' e.g. enter your name: 'Fenix'


# Running tests

    python test.py

# Schema

Ferry : list of ferries the company have
VehicleType: list of possible vehicle types (boarding_price, minimum gas it should have to avoid going to gas station)
ferryvehicletype: relationship between ferries and vehilce types e.g. Ferry A can carry 3 cars, 4 vans
employee: employee details
employee_income: income employee makes
vehicles: list of individual vehicles, identified by plate number
route_types: route types (i.e. stations) where vehicles stops such as gas stations, customs etc.
services: services stareted by vehicles
routes: stops a vehicle makes from arrival to boarding on ferry ( e.g. going to gas station, customs etc)



# Question 1: adding a new employee

Employees are stored separately and their payment/income is calculated in isolation. Hence, adding an employee won't affect the design. All one has to do is state the amount the employee is supposed to make. E.g. 11 %. Income is calculated based on boarding price of a vehicle type, which is also dynamic.

# Question 2: New Station

Stations (named routetypes) are stored in a separate entity, hence the change is minimal. Currently, we state if a station is a gas_station or customs office. The design would be improved by making the tablet as generic as possible. Hence, the first change I would make would be to the table:

    station_name station_type

where station_type can be gas_station, battery_recharging etc.

The advantage of such a design is that we can add more logic based on type. e.g. we have method stopAtGasStation which is called only when a car stops at a gas stations. Leaving all stations out, we can apply gas-station only logics and requirments here, such as asking for gas and so forth.

# Question 3: Adding Ferry and Vehicle Type

Then change would very minimal. The current design stores ferries and vehicle types separately then relates them. For e.g. we might have Small Ferry. All we care about is how many electric cars or vans it can carry. Vehicle types have their own properties. For e.g. all cars might have to pay $3 and go to the gas_station if their gas is below 10%.

Now the change I would make would be to vehicletypes model by adding a column type (for e.g. electrical car, hybrid etc). Of course that is assuming we have a finite number of types of vehicles.
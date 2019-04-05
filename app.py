import sys
import sqlite3
from datetime import date
from utilities import showDirections , drawTable ,dbRowsToDict
import random

test_mode = True #we are in test mode

def get_input(text):
    return input(text)
    

class DBOperation():
    '''
    Class to handle database operations
    '''
    connection = None # not yet connected
    connection_is_open = False

    def __init__(self):
        '''
        As we initialize, check if database has been created already or not?
        '''
        db = 'db.db' if not test_mode else 'db_test.db'

        try:
            self.connection = sqlite3.connect(db)

            self.connection.execute("PRAGMA foreign_keys = 1")
            # create the database now since this is brand new connection
            self.connection_is_open = True
            
        except:
            print('Error connecting to database')
            self.connection_is_open = False
        finally:
            
            pass
        

    
    def close(self, dude = ''):
        '''
        Close the database
        '''

        try:
            self.connection_is_open = False
            self.connection.close()
        except:
            # closing a closing object
            self.connection_is_open = False
        
        

    
    def createDatabase(self):
        '''
        Creates the database models.
        '''
        
        ferryTable = """ CREATE TABLE IF NOT EXISTS ferry (
                                            id integer PRIMARY KEY AUTOINCREMENT,
                                            name text NOT NULL
                                        ); """
    
        vehicleTypeTable = """CREATE TABLE IF NOT EXISTS vehicletype (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        name text NOT NULL UNIQUE,
                                        min_gas integer,
                                        boarding_price integer
                                    );"""
        
        ferryVehicleTypeTable = """CREATE TABLE IF NOT EXISTS ferryvehicletype (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        ferry_id int,
                                        vehicletype_id int,
                                        max_number integer,
                                        FOREIGN KEY (ferry_id) REFERENCES ferry (id),
                                        FOREIGN KEY (vehicletype_id) REFERENCES vehicletype (id)
                                    );"""


        employeeTable = """CREATE TABLE IF NOT EXISTS employee (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        name text,
                                        ticket_percentage int,
                                        password int,
                                        emp_code int
                                    );"""

        employeeIncomesTable = """CREATE TABLE IF NOT EXISTS employee_incomes (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        employee_id int,
                                        paid_on text,
                                        amount real,
                                        FOREIGN KEY (employee_id) REFERENCES employee (id)
                                    );"""

        vehicleTable = """CREATE TABLE IF NOT EXISTS vehicle (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        vehicletype_id int,
                                        platenumber text,
                                        gas_capacity int,
                                        FOREIGN KEY (vehicletype_id) REFERENCES vehicletype (id)
                                    );"""

        routeTypesTable = """CREATE TABLE IF NOT EXISTS routetype (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        name text not null unique,
                                        requires_open_door int default 0,
                                        is_gas_station int default 0,
                                        is_customs int default 0,
                                        route_order int
                                    );"""

        serviceTable = """CREATE TABLE IF NOT EXISTS service (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        vehicle_id int,
                                        employee_id int,
                                        service_code text,
                                        registered_on text,
                                        amount real,
                                        gas_level int,
                                        status int default 1,
                                        door_status int default 0,
                                        FOREIGN KEY (vehicle_id) REFERENCES vehicle (id),
                                        FOREIGN KEY (employee_id) REFERENCES employee (id)
                                    );"""
        
        routeTable = """CREATE TABLE IF NOT EXISTS routes (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        service_id int,
                                        route_type_id int,
                                        door_status int default 0,
                                        gas_taken int default 0,
                                        registered_on int,
                                        FOREIGN KEY (service_id) REFERENCES service (id),
                                        FOREIGN KEY (route_type_id) REFERENCES routetype (id)
                                    );"""        

        cursor = self.connection.cursor()
        cursor.execute(ferryTable)
        cursor.execute(vehicleTypeTable)
        cursor.execute(ferryVehicleTypeTable)
        cursor.execute(employeeTable)
        cursor.execute(employeeIncomesTable)
        cursor.execute(vehicleTable)
        cursor.execute(routeTypesTable)
        cursor.execute(serviceTable)
        cursor.execute(routeTable)
        cursor.close()

        #close the database now
        self.close()
        print('The database has been created successfully')


class Routes:
    '''
    Manage the route a vehicle might take to be on board
    i.e. gas station, customs
    '''
    routes_found = False
    

    def __init__(self, show_dialog = True):
        '''
        Wants something to do with routes management
        @input show_dialog : boolean. Do we need to show directions dialog?
        '''
        if show_dialog:
            directions = [
                '      - Type list to list existing routes',
                '      - type add to add new route'
                ]
            showDirections(directions, test_mode)
            reply = get_input('What do you want to do? ').strip()


            if reply == 'list':
                self.showRoutes()
            
            elif reply == 'add':
                self.addRoute()

    def showRoutes(self):
        '''
        Show routes we have in the app
        '''

        db = DBOperation()      
        cursor = db.connection.cursor()
        cursor.execute("SELECT * FROM routetype ORDER BY route_order")
        records_info = dbRowsToDict(cursor)
        rows = records_info['rows']
        if rows:
            self.routes_found = True

        drawTable(records_info['columns'], rows, 'List of Registered Routes', test_mode)

        db.close()
        
        return rows
    
    def maxOrder(self):
        '''
        Return the route with the higest order (i.e. visited last during the boarding)
        '''
        route_order = 0 # assume we have no route type and this will be first entry
        db = DBOperation()
        cursor = db.connection.cursor()
        cursor.execute('SELECT MAX(route_order) as max_order FROM routetype')
        records_info = dbRowsToDict(cursor)
        rows = records_info['rows']
        if rows and rows[0]['max_order'] is not None:
            route_order = rows[0]['max_order']
        
        db.close()

        return route_order

    def addRoute(self):
        '''
        Add a new route
        '''
        route_id = 0 #not yet added
        db = DBOperation()
        name = get_input('Add name of the new route ').strip()
        requires_open_door = get_input('Must the door of vehicle be open at the route? (y/n): ').strip()
        is_gas_station = get_input('Is this a gas station? (y/n): ').strip()
        is_customs = get_input('Is this customs? (y/n): ').strip()

        
        # is it unique?
        cur = db.connection.cursor()
        cur.execute("SELECT * FROM routetype WHERE name=?", (name,))
 
        rows = cur.fetchall()

        errs = []
        
        if len(rows)>0:
            errs.append('Route names must be unique. Please try again')
        
        is_gas_station = 1 if is_gas_station=='y' else 0
        is_customs = 1 if is_customs =='y' else 0 
        requires_open_door= 1 if requires_open_door =='y' else 0

        # it cant be both a gas station or custom?
        if is_gas_station == 1 and is_customs ==1:
            errs.append('A route cannot be a gas station and customs at the same time')
        
        if errs:
            raise Exception(errs)
        
        else:
            route_order = self.maxOrder() + 1
            cur.execute('INSERT INTO routetype (name, is_gas_station,is_customs, requires_open_door, route_order ) VALUES (?,?,?,?,?) ', (name,is_gas_station,is_customs, requires_open_door, route_order))
            db.connection.commit()
            print('The route was added successfully')
            route_id = cur.lastrowid
        
        cur.close()
        db.close()

        return route_id


class Employee:
    '''
    Manage employees of the company
    '''
    employees_found = False
    

    def __init__(self, show_dialog = True):
        '''
        
        @input show_dialog : boolean. Do we need to show directions dialog?
        '''
        if show_dialog:
            directions = [
                '      - Type list to list existing employes',
                '      - type add to add new employee randomly'
                ]
            showDirections(directions, test_mode)
            reply = get_input('What do you want to do? ').strip()

            if reply == 'list':
                
                self.showEmployees(show_dialog)
            
            elif reply == 'add':
                self.addEmployee()

    def showEmployees(self, show_dialog = False):
        '''
        Show employees we have in the app
        '''
        db = DBOperation()
        
        cursor = db.connection.cursor()
        cursor.execute("SELECT * FROM employee ORDER BY name")

        records_info = dbRowsToDict(cursor)
 
        rows = records_info['rows']
        db.close()

        drawTable(records_info['columns'], rows, 'List of Registered Employees', test_mode)
       
        if rows:
            self.employees_found = True
            if show_dialog:
                employee_id = get_input('To see employee income report, enter employee id: ')
                if employee_id != 'q':
                    self.employeeIncomeReports(employee_id)


        return rows
    
    def employeeIncomeReports(self, employee_id):
        '''
        Print income an employee has made so far
        '''
        db = DBOperation()
        cursor = db.connection.cursor()
        cursor.execute('SELECT amount,paid_on FROM employee_incomes WHERE employee_id=? ORDER BY id', (employee_id,))
        records_info = dbRowsToDict(cursor)
        drawTable(records_info['columns'], records_info['rows'], 'Employee Income Basic Report', test_mode)

        db.close()


    def addEmployee(self):
        '''
        Add a new employee.
        '''
        new_employee_id = 0
        name = get_input('Add name of the new employee ').strip()
        ticket_percentage = get_input('Enter percentage cut of employee for each vehicle serviced: ')

        try:
            ticket_percentage = int(ticket_percentage)
        except:
            ticket_percentage=-1
        
        if ticket_percentage<0:
            raise Exception('Percentage cut cannot be less than 0')
        
        db = DBOperation()
        cur = db.connection.cursor()
        password = 12345
        emp_code = self.generateEmployeeCode()
        cur.execute('INSERT INTO employee (name, ticket_percentage,password, emp_code ) VALUES (?,?,?,?) ', (name,ticket_percentage, password, emp_code))
        db.connection.commit()
        new_employee_id = cur.lastrowid
        print('The employee was added successfully with Employee Code ', emp_code)
        
        cur.close()
        db.close()

        return new_employee_id
    
    def generateEmployeeCode(self):
        '''
        Generate employee id to be used as a username
        '''
        return random.randint(1000,2000)
    
    def employeeLogin(self, emp_code, password):
        '''
        Login the employee to the system
        @input emp_code: username/employee code
        @input password

        @output empty object if emp_code and password are wrong. Else, returns employee detail

        '''
        db = DBOperation()
        cursor = db.connection.cursor()
        cursor.execute('SELECT * FROM employee WHERE password=? AND emp_code=?', (password, emp_code))
        records_fetcher = dbRowsToDict(cursor)
        db.close()
        return records_fetcher['rows']
    
    def addEmployeeIncome(self, employee_id, amount):
        '''
        Pay the employee
        '''
        new_employee_id = 0
        db = DBOperation()
        cursor = db.connection.cursor()
        cursor.execute('INSERT INTO employee_incomes (employee_id,amount, paid_on) VALUES(?,?,?)', (employee_id, amount, date.today()) )
        db.connection.commit()
        new_employee_id = cursor.lastrowid
        cursor.close()
        db.close()

        return new_employee_id




class Ferry:
    '''
    Manage ferries we have
    '''
    ferries_found = False
    

    def __init__(self, show_dialog = True):
        '''
        Wants something to do with ferries management
        @input show_dialog : boolean. Do we need to show directions dialog?
        '''
        if show_dialog:
            directions = [
                '      - Type list to list ferries',
                '      - type add to add new ferry'
                ]
            showDirections(directions)
            reply = get_input('What do you want to do? ').strip()

            if reply == 'list':
                
                self.showFerries()
            
            elif reply == 'add':
                self.addFerry()

    def showFerries(self, show_dialog = True):
        '''
        Show ferries we have in the app
        @input show_dialog : boolean. If there are ferries, do we need to show dialog to manage them?
        '''
        db = DBOperation()
        
        cursor = db.connection.cursor()
        cursor.execute("SELECT * FROM ferry")

        records_info = dbRowsToDict(cursor)
 
        rows = records_info['rows']

        if rows:
            self.ferries_found = True
        
        drawTable(records_info['columns'], rows, 'List of Registered Ferries', test_mode)


        db.close()

        if show_dialog and rows:
            # we have ferries so we can attach the types to vehicletypes here
            id = get_input('To set ferry - vehicle setting, type in the id of the ferry ')
            if id =='q':
                sys.exit()
            else:
                FerryVehicleSetting('ferry', id)    

    def addFerry(self):
        '''
        Add a new ferry
        '''
        db = DBOperation()
        name = get_input('Add name of the new ferry ').strip()
        # is it unique?
        cur = db.connection.cursor()
        cur.execute("SELECT * FROM ferry WHERE name=?", (name,))
 
        rows = cur.fetchall()
        
        if len(rows)>0:
            raise Exception('Ferry names must be unique. Please try again')
        else:
            cur.execute('INSERT INTO ferry (name) VALUES (?) ', (name,))
            db.connection.commit()
            print('The ferry was added successfully')
        
        cur.close()
        db.close()




class VehicleType:
    '''
    Vehicle Types we serve such as cars, vans etc
    '''
    vehicles_found = False
    
    def __init__(self, show_dialog = True):
        '''
        @input show_dialog: boolean. Do we need to ask the user what he/she wants to do?
        
        '''
        if show_dialog:
            directions = [
                '      - Type list to list vehicle types',
                '      - type add to add new vehicle type'
                ]
            showDirections(directions)
            reply = get_input('What do you want to do? ').strip()

            if reply == 'list':
                self.showVehicleTypes()
            
            elif reply == 'add':
                self.addVehicleType()
    
    def showVehicleTypeInfo(self , id):
        '''
        Return information of a specific vechile
        '''
        db = DBOperation()
        cur = db.connection.cursor()
        cur.execute("SELECT * FROM vehicletype WHERE id=?", (id,))

        records_info = dbRowsToDict(cur)
        
        rows = records_info['rows']
    
        db.close()
        if rows:
            return rows[0]
        
        return None   

    def showVehicleTypes(self, show_dialog = True):
        '''
        Show vehicles types we have in the app
        @input show_dialog: boolean. If there are registered vehicle types, should user be allowed to select one for management?
        '''
        db = DBOperation()
        
        cur = db.connection.cursor()
        cur.execute("SELECT * FROM vehicletype")

        records_info = dbRowsToDict(cur)
 
        rows = records_info['rows']

        drawTable(records_info['columns'], rows, 'List of Vehicle Types')

        db.close()

        if rows:
            self.vehicles_found = True
        
        if show_dialog and rows:
            # we have vehicle types so we can attach the types to ferries here
            id = get_input('To set ferry - vehicle setting, type in the id of the vehicle type: ')
            
            if id =='q':
                sys.exit()
            else:
                FerryVehicleSetting('vehicle_type', id)
        

    def addVehicleType(self):
        '''
        Add a new vehicle type
        '''
        db = DBOperation()
        name = get_input('Add name of the new vehicle type: ').strip()
        min_gas = get_input('Enter the min gas vehicle to have to be forced to go to gas station: ')
        boarding_price = get_input('Enter price to board a ferry: ')
        # is it unique?
        cur = db.connection.cursor()
        cur.execute("SELECT * FROM vehicletype WHERE name=?", (name,))
 
        rows = cur.fetchall()

        errs =[]
        
        if len(rows)>0:
            errs.append('Vehicle type name must be unique. Please try again')

        try:
            min_gas = float(min_gas)
        except:
            min_gas = 0
        
        if not isinstance(min_gas, float) or min_gas<0:
            errs.append('Min gas must be at least 1 percent')    

        try:
            boarding_price = float(boarding_price)
        except:
            boarding_price = 0
        
        if not isinstance(boarding_price, float) or min_gas<0:
            errs.append('Boarding price must be at least 1UGS') 

        if errs:
            raise Exception(errs)   
        
        else:
            cur.execute('INSERT INTO vehicletype (name,min_gas, boarding_price) VALUES (?, ?, ?) ', (name,min_gas, boarding_price))
            db.connection.commit()
            print('The vehichle type was added successfully')
        
        cur.close()
        db.close()



class FerryVehicleSetting:
    '''
    Load settings of a ferry with regards to vehicle types.
    For flexiblity, the association between the two can come
    from either
    '''
    
    def __init__(self, source_type, record_id):
        '''
        @input source_type: string. ferry if calling from ferries i.e. record_id is from ferry model.
                                    else vehicleid
        @input record_id: id from ferry or vehicletype 
        '''

        db = DBOperation()
        cursor = db.connection.cursor()
        #get current settings based on field type

        
        if source_type == 'ferry':
            cursor.execute('SELECT * FROM ferryvehicletype WHERE  ferry_id=?', ( record_id, )  )
        else:
            cursor.execute('SELECT * FROM ferryvehicletype WHERE  vehicletype_id=?', ( record_id, )  )
        
        records_info = dbRowsToDict(cursor)

        rows = records_info['rows']

        drawTable(records_info['columns'], rows,'Ferries vs Vehicle Types Relationship')
        
        db.close()
        #incase user wants to create associations, display ferries or types
        
        if source_type == 'ferry':
            # we are viewing ferry here. So display vehicle types
            source = VehicleType(False)
            source.showVehicleTypes(False)
            # do we have vehicle types to attach with the active ferry with?
            
            if source.vehicles_found:
                vehicle_id = get_input('Enter the vehicle type you want to relate with a ferry with or q to quit ')
                if vehicle_id=='q':
                    sys.exit()
                self.createRelationships(vehicle_id,record_id)
                

        elif source_type =='vehicle_type':
            # we are viewing vehicle type here. So display ferries to attach it with
            source = Ferry(False)
            source.showFerries(False)
            
            if source.ferries_found:
                ferry_id = get_input('Enter the ferry id you want to relate with a vehicle with or q to quit ')
                if ferry_id == 'q':
                    sys.exit()
                self.createRelationships(ferry_id,record_id)


    def createRelationships(self, ferry_id, vehicle_type_id):
        '''
        Create relationships between a ferry and a vehicle type:
        how many vehicle_type can a ferry carry at most?
        @input ferry_id: the id of the ferry to work with
        @input vehicle_type_id: the id of the vehicle_type_id

        Both must exist already but the relationship will be updated if it exists
        '''
        max_allowed = get_input('Enter the maximum number of the vehicle types the ferry can carry ')
        # max_allowed must be integer
        try:
            max_allowed = int(max_allowed)
        except:
            max_allowed = 0
        
        if max_allowed<=0:
            raise Exception('Maximum number of vehicle type that can be loaded on a ferry must be above zero')
        
        db = DBOperation()
        cursor = db.connection.cursor()

        cursor.execute('SELECT id FROM ferryvehicletype WHERE ferry_id=? AND vehicletype_id=?', (ferry_id, vehicle_type_id))
        rows = cursor.fetchall()

        if not rows:
            cursor.execute('INSERT INTO ferryvehicletype (ferry_id, vehicletype_id, max_number) VALUES(?,?,?)', (ferry_id, vehicle_type_id, max_allowed))
            db.connection.commit()
            print('Relationship created')
        else:
            cursor.execute('UPDATE ferryvehicletype SET ferry_id =?, vehicletype_id=?, max_number=? WHERE ferry_id=? AND vehicletype_id=?', (ferry_id, vehicle_type_id, max_allowed,ferry_id, vehicle_type_id))
            print('Relationshp updated ok')

        cursor.close()
        db.close()


class Vehicle:
    '''
    Vehicles who come to be boarded to ferries
    '''
    vehicles_found = False
    
    def __init__(self):
        '''
        
        '''
        self.vehicles_found = False
        pass


    def showVehicles(self, return_one = False):
        '''
        Show vehicles we have in the app
        @input return_one: boolean. Do we need to return a vehicle? If we have one vehicle only
                    return it. Else, ask the user to select one

        @output dictionary if return_one = True, else an array of dictionaries of records
        '''
        plate_number = get_input('Enter the plate number of the vehicle you want to search: ')

        db = DBOperation()
        
        cur = db.connection.cursor()
        if not plate_number:
            cur.execute("SELECT * FROM vehicle")
        else:
            cur.execute("SELECT * FROM vehicle WHERE platenumber=?", (plate_number,))
 
    
        records_info = dbRowsToDict(cur) #diciontary data
        rows = records_info['rows']
        drawTable(records_info['columns'], rows, 'List of Vehicles')
        found_vehicles = len(records_info['rows'])

        db.close()

        if found_vehicles>0:
            self.vehicles_found = True
            #if it is one vehicle return it

            if return_one:
                # until user selects one of the list vehicles or cancels
                selected_vehicle = 0
                while selected_vehicle==0:
                    
                    value = get_input('Enter the ID of the vehicle you want to work with or q to quit: ')
                    if value == 'q':
                        return {}
                    else:
                        # it must exist
                        counter = 0
                        for row in rows:
                            if row['id'] == value:
                                selected_vehicle = row['id']
                                return rows[counter]
                            counter = counter + 1
            else:
                return rows
                
                    
        
        else:
            if return_one:
                return {} # we didnt find
            
            return []

    def showVehicleInfo(self, id):
        '''
        Return vehicle information of a specific vehicle
        @input id: id of the vehicle whose information you want
        '''
        db = DBOperation()
        cur = db.connection.cursor()
        cur.execute('SELECT * FROM vehicle WHERE id=?', (id,))
        records_info = dbRowsToDict(cur)

        db.close()
        if records_info['rows']:
            return records_info['rows'][0]
        return None
            

    def addVehicle(self):
        '''
        Add a new vehicle
        '''
        print('Follow the questions to add a new vehicle. A vehicle can be of the following registered type only')
        vehicle_type = VehicleType(False)

        vehicle_type.showVehicleTypes(False)

        if not vehicle_type.vehicles_found:
            print('To add vehicles, you must add vehicle types first')
            return []
            sys.exit()

        db = DBOperation()
        plate_number = get_input('Add plate of the vehicle: ')
        gas_capacity = get_input('Enter the gas/fuel capacity of the vehicle: ')
        vehicletype_id = get_input('From the list above, select the vehicle type ID: ')
        # if plate number exists, simply return its id in the database

        # is it unique?
        cur = db.connection.cursor()
        cur.execute("SELECT * FROM vehicle WHERE platenumber=?", (plate_number,))
 
        records_info = dbRowsToDict(cur)
        if len(records_info['rows'])>0:
            db.close()
            return records_info['rows'][0]
        
        # doesn't exist. so confirm data is basically fine
        try:
            gas_capacity = float(gas_capacity)
        except:
            gas_capacity = 0
        
        if gas_capacity<=0:
            raise Exception('Gas capacity of a vehicle must be greater than 0')
        
        cur = db.connection.cursor() #rember dbRowsToDict closes curors

        cur.execute('INSERT INTO vehicle (platenumber,vehicletype_id, gas_capacity ) VALUES (?, ?, ?) ', (plate_number, vehicletype_id, gas_capacity))

        db.connection.commit()
        new_id = cur.lastrowid
        added_vehicle_info = []
        if new_id >0:
            # added successfully. return the object now.
            added_vehicle_info = self.showVehicleInfo(new_id)
        else:
            print('There was an error adding the vehicle')
            
        print('The vehichle was added successfully with id ', new_id, ' . Please continue servicing the vehicle now')
        
        cur.close()
        db.close()
        return added_vehicle_info



class BoardingService:
    '''
    Handles new boarding services for vehicles to go into ferries
    '''

    def __init__(self, show_dialog = True):
        '''
        @input show_dialog: boolean. Do we need to ask the user what he/she wants to do?
        
        '''
        if show_dialog:
            directions = [
                '      - Type start to board a new vehicle',
                '      - type list existing boarding services'
                ]
            showDirections(directions)
            reply = get_input('What do you want to do? ').strip()

            if reply == 'start':
                self.start()
            
            elif reply == 'list':
                self.showBoardings()
    
    def showBoardings(self):
        '''
        Show boardings of vehicles
        '''
        db = DBOperation()
        cursor = db.connection.cursor()
        cursor.execute('SELECT service.id AS service_id, service.amount AS boarding_price,service.registered_on AS registered_on,service.gas_level AS gas_level, vehicle.gas_capacity AS gas_capacity, vehicle.platenumber AS plate_number,employee.name AS emp_name, employee.emp_code AS employee_code,employee.ticket_percentage, ((1.0 * employee.ticket_percentage)/100) * vehicletype.boarding_price AS employee_cut FROM service,vehicle,employee,vehicletype WHERE vehicletype.id= vehicle.vehicletype_id AND vehicle.id=service.vehicle_id AND service.employee_id=employee.id ORDER BY service.id DESC')
        
        records = dbRowsToDict(cursor)
        drawTable(records['columns'], records['rows'], 'List of Boarding Services')
        db.close()
        if records['rows']:
            #give user the option to view routes taken by a specific vehicle
            service_id = get_input('To view routes covered by a specific service, enter its id: ')
            if service_id!='q':
                self.routesCovered(service_id)
            else:
                sys.exit()

        




    def start(self):
        '''
        A vehicle just arrived to the gate to be boarded
        '''
        print('You are about to board a new vehicle to a ferry')

        employee_code = get_input('Please enter your employee code: ')
        password = get_input('Please enter your password: ')
        
        employee = Employee(False)
        employee_info = employee.employeeLogin(employee_code, password)
        if not employee_info:
            print('Your user details are not correct. Please start again')
            sys.exit()
        
        employee_info = employee_info[0]

        
        #
        option = get_input('Is this a new vehicle? (y/n): ').strip()
        self.vehicle_info = []
        vehicle = Vehicle()
        if option == 'y':
            # the vehicle is new so register it now
            self.vehicle_info = vehicle.addVehicle()
        else:
            # it has been in service before. get its information
            
            self.vehicle_info = vehicle.showVehicles(True)
        if self.vehicle_info:
            # we got our car so time to ask questions
            gas_level = get_input('Enter the gas/fuel level of the vehicle at entry gate: ')
            if gas_level == 'q':
                sys.exit()

            try:
                gas_level = float(gas_level)
            except:
                gas_level = 0
            
            # what percentage of its tank is full now?


            if gas_level>self.vehicle_info['gas_capacity']:
                print('The vehicle can store maximum ', self.vehicle_info['gas_capacity'], ' fuel. Please try again')
                sys.exit()
            

            
            # get routes a vehicle needs to take to board on a ferry
            registered_routes = Routes(False)
            self.routes = registered_routes.showRoutes() # an array dictionary
            if not self.routes:
                print('You must add routes first to board vechiles to ferries')
                sys.exit()

            # we need to know the boarding price of the vehicle based on its type
            vehicle_type = VehicleType(False)
            self.vehicle_type_info = vehicle_type.showVehicleTypeInfo(self.vehicle_info['vehicletype_id'])
            if self.vehicle_type_info is None:
                # for some reason, we cant get it
                print('There was an error getting vehicle type info')
                sys.exit()
            #register the vehicle for boarding attempt here

            amount = self.vehicle_type_info['boarding_price'] # this is what the car pays to the company
            employee_cut = (float(employee_info['ticket_percentage']) / 100) * amount # pay the employee this amount
            employee.addEmployeeIncome(employee_info['id'], employee_cut)

            service_code= self.generateServiceCode()
            db = DBOperation()
            cursor = db.connection.cursor()
            cursor.execute('INSERT INTO service (vehicle_id, employee_id, gas_level, service_code, status, amount) VALUES(?,?,?,?,0,?)', (self.vehicle_info['id'], employee_info['id'] , gas_level, service_code, amount))
            db.connection.commit()
            service_id = cursor.lastrowid

            cursor.close()
            db.close()

            if service_id is not None and service_id>0:
                #pay the employee first
                print('The vehicle is up for boarding service with service code ', service_code)
                #now take it step by step
                service = self.serviceInfo(service_id)
                for route in self.routes:
                    if route['is_gas_station'] == 1:
                        #we are in gas station
                        
                        self.stopAtGasStation(service)
                    elif route['is_customs'] == 1:
                        # we in customs office
                        self.stopAtCustoms(service, route)
                
                # print the routes taken by the vehicle now
                self.routesCovered(service_id)


    
    def serviceInfo(self, service_id):
        '''
        Return information about the service
        '''
        db = DBOperation()
        cur = db.connection.cursor()
        cur.execute('SELECT * FROM service WHERE id=?', (service_id,))
        records_info = dbRowsToDict(cur)

        db.close()
        if records_info['rows']:
            return records_info['rows'][0]
        return None
    

    def setDoorStatus(self, service, route):
        '''
        Some routes require the door to be open for service?
        @input service: Object. The service we are checking.
        @input route: Route object.

        @output: Boolean. True if door is currently open or false
        '''
        reply = -1 #we dont know its state. 1 is closed door, 0 is open door

        if route['requires_open_door']==1:

            if service['door_status'] == 0:
                # the door must be open
                while reply == -1:
                    value = get_input('The route requires the door to be open. Did you open the door now? (y/n): ')
                    if value == 'y':
                        reply = 1
                        break
            else:
                reply = 0 # making sure we dont return -1 cos the conditions fail
        else:
            if service['door_status'] == 1:
                # the door must be open
                while reply == -1:
                    value = get_input('The route requires the door to be closed. Did you open the close now? (y/n): ')
                    if value == 'y':
                        reply = 0
                        break
            else:
                reply = 0
        #update the door status of the vehicle now
        db = DBOperation()
        cursor = db.connection.cursor()
        cursor.execute('UPDATE service SET door_status=? WHERE id=?', (service['id'], reply))
        db.connection.commit()
        cursor.close()
        db.close()
        return reply
    


    def updateServiceStatus(self):
        '''
        Update status of the service
        '''
        pass
    

    def stopAtCustoms(self, service, customs_office):
        '''
        Stop at customs office here
        '''
        # make sure door requirement is satisified
        door_status = self.setDoorStatus(service, customs_office)
        # add the route now
        db = DBOperation()
        cursor = db.connection.cursor()
        cursor.execute('INSERT INTO routes (service_id, route_type_id, door_status) VALUES(?,?,?) ', (service['id'], customs_office['id'], door_status))
        db.connection.commit()
        
        route_id =0 #assume not added
        if cursor.lastrowid is not None:
            route_id = cursor.lastrowid
        cursor.close()
        db.close()
        return route_id
  
    
    def stopAtGasStation(self, service):
        '''
        Vehicle is stopping at gas station

        Expansion: do we need to know how many liters was taken and its price?
        Anything related to filling gas should be handled here
        '''
        #Do we need to first buy gas? How much percentage of its capacity is full?
        percentage_avaliable = (service['gas_level'] / self.vehicle_info['gas_capacity']) * 100
        if percentage_avaliable >= self.vehicle_type_info['min_gas']:
            #it has enough gas in its gas tank so need to stop by the gas station
            return 0

        # first check if the vehicle has taken gas. If it has already been here
        # not need to be here
        db = DBOperation()
        cursor = db.connection.cursor()
        cursor.execute('SELECT routes.id AS id FROM routes,routetype WHERE routetype.id=routes.route_type_id AND service_id=?', (service['id'],))
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        if len(rows)>0:
            for row in rows:
                return row['id']
        
        #we didn't yet
         
        selected_gas_station = 0 #not yet selected
        value = 0
        while selected_gas_station == 0:
            value = get_input('The vehicle needs to go to the gas station. Enter the gas station to send it to: ')
            # is it a gas station
            for route in self.routes:
                if route['is_gas_station'] == 1 and route['id']==value:
                    selected_gas_station = route
                    break
        
        # before giving gas, lets force open/close the door based on the route and update it
        door_status = self.setDoorStatus(service, selected_gas_station)

        
        gas_taken = get_input('Enter gas liters taken?: ')
        try:
            gas_taken = float(gas_taken)
        except:
            gas_taken = 0
        
        if gas_taken<=0:
            raise Exception('Gas taken must be above 0 liters')

        
        db = DBOperation()
        cursor = db.connection.cursor()
        cursor.execute('INSERT INTO routes (service_id, route_type_id, door_status, gas_taken) VALUES(?,?,?,?) ', (service['id'], selected_gas_station['id'], door_status, gas_taken))
        db.connection.commit()
        
        route_id =0 #assume not added
        if cursor.lastrowid is not None:
            route_id = cursor.lastrowid
        cursor.close()
        db.close()
        return route_id




    def generateServiceCode(self):
        '''
        Generate a unique service code
        '''
        return random.randint(1000001,99999999)

    def addRoute(self, service_id, route_type_id):
        '''
        Add a route to a specific service
        '''
        db = DBOperation()
        cursor = db.connection.cursor()
        cursor.execute('INSERT INTO routes (service_id, route_type_id, door_status) VALUES(?,?,?) ', (service_id, route_type_id, 0))
        db.connection.commit()
        db.close()
        route_id =0 #assume not added
        if cursor.lastrowid is not None:
            route_id = cursor.lastrowid
        cursor.close()
        return route_id
    
    def routesCovered(self, service_id):
        '''
        Print out the destinations taken already for the vehicle
        '''
        db = DBOperation()
        cursor = db.connection.cursor()
        cursor.execute('SELECT routetype.name AS route_name , routes.door_status AS door_status FROM routes,routetype WHERE routes.route_type_id=routetype.id AND routes.service_id=? ORDER BY routes.id', (service_id,))
        records_fetcher = dbRowsToDict(cursor)
        drawTable(records_fetcher['columns'], records_fetcher['rows'], 'Path Taken By Vehicle')

        db.close()





if __name__ == "__main__":
    print('Welcome to Ferry. For list of commands type h')
    # connect to the database

    test_mode = False

    print(test_mode, 'test modecls')

    command = '' # default command will be help

    if len(sys.argv)>1:
        command = sys.argv[1]
    
    if command == 'create':
        db = DBOperation()
        db.createDatabase()
    
    elif command == 'ferry':
        Ferry()
    
    elif command == 'routes':
        Routes()
    
    elif command == 'nv':
        VehicleType()
    
    elif command == 'service':
        boarding_service = BoardingService(True)
    
    elif command == 'employee':
        Employee()

    else:
        #wants help
        directions = [
            '   - type create to create the database for first time',
            '   - type nv to manage vechile type',
            '   - type init to initialize the database with sample data (you will lose existing data)',
            '   - type routes to manage routes vehicles take from arrival to boarding',
            '   - type ferry to manage your ferries',
            '   - type employee to manage employees',
            '   - type service to start a new boarding service',

        ]
        showDirections(directions)
    
    





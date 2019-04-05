import unittest
import os
from app import DBOperation, Routes, Employee
from unittest.mock import patch

class aInitalizeTestCase(unittest.TestCase):
    '''
    Prepare test case. Delete the file here if
    it exists
    '''
    try:
        os.remove('db_test.db')
    except:
        pass
    

class bDBCreationTestCase(unittest.TestCase):
    """Tests for db file/memory existintence """

    def test_dbCreation(self):
        """Did we create our database?"""
        db = DBOperation()
        self.assertTrue(db.connection)
        db.createDatabase()
        self.assertFalse(db.connection_is_open)

class cRoutesTestCase(unittest.TestCase):
    """Tests for routes """

    @patch('app.get_input', return_value='list')
    def test_azeroRoutes(self, input):
        """we shouldn't have any routes defined"""
        routes = Routes(True)
        self.assertFalse(routes.routes_found)

    def test_bmaxRouteOrder(self):
        """Max order must be 0"""
        routes = Routes(False)
        self.assertEqual(routes.maxOrder(), 0)


    @patch('app.get_input')
    def test_caddNewRoute(self, input_mock):
        """add new route"""
        routes = Routes(False)
        input_mock.side_effect = ['Gas Station', 'n', 'y', 'n']
        new_route_id = routes.addRoute()
        self.assertEqual(routes.maxOrder(), 1)
        self.assertEqual(new_route_id, 1)
        routes.showRoutes()
        self.assertTrue(routes.routes_found)

class dEmployeeTestCase(unittest.TestCase):
    """Test case for employees """

    
    @patch('app.get_input', return_value='list')
    def test_azeroEmployees(self, input):
        """we shouldn't have any employees registered"""
        employees = Employee(True)
        self.assertFalse(employees.employees_found)


    def test_cgenerateEmployeeCode(self):
        """Test employee code generator"""
        employee = Employee(False)
        code = employee.generateEmployeeCode()
        self.assertEqual(type(code), int)
        self.assertEqual(len(str(code)), 4)

    @patch('app.get_input')
    def test_daddEmployee(self, input_mock):
        """add new employee"""
        
        employee = Employee(False)
        input_mock.side_effect = ['FenixEmployeer',3]
        new_employee_id = employee.addEmployee()
        self.assertEqual(new_employee_id, 1)    
        
    def test_eloginEmployee(self):
        """login employee"""
        employee = Employee(False)

        bad_login = employee.employeeLogin(1234, 0000)
        
        employee_detail = employee.showEmployees(False)[0]
        good_login = employee.employeeLogin(employee_detail['emp_code'], 12345)

        self.assertEqual(len(bad_login), 0)
        self.assertEqual(len(good_login), 1)

    def test_eaddEmployeeIncome(self):
        """add income/salary of the mployee"""
        employee = Employee(False)
        auto_id = employee.addEmployeeIncome(1, 30)
        self.assertEqual(auto_id,1)
        

if __name__ == '__main__':
    unittest.main()
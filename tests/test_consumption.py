from eemeter.consumption import Consumption
from eemeter.consumption import FuelType
from eemeter.consumption import electricity
from eemeter.consumption import natural_gas
from eemeter.consumption import propane
from eemeter.consumption import DateRangeException
from eemeter.consumption import InvalidFuelTypeException
from eemeter.consumption import ConsumptionHistory

from datetime import datetime
from pint.unit import UndefinedUnitError

import pytest

EPSILON = 1e-6
##### Fixtures #####

@pytest.fixture(scope="module",
                params=[(0,"kWh",electricity,datetime(2000,1,1),datetime(2000,1,31),False),
                        (0.0,"kWh",electricity,datetime(2000,1,1),datetime(2000,1,31),False),
                        (0.0,"therms",electricity,datetime(2000,1,1),datetime(2000,1,31),False),
                        (0.0,"Btu",electricity,datetime(2000,1,1),datetime(2000,1,31),False),
                        (0.0,"Btu",natural_gas,datetime(2000,1,1),datetime(2000,1,31),False),
                        (0.0,"therms",natural_gas,datetime(2000,1,1),datetime(2000,1,31),False),
                        (0.0,"Btu",natural_gas,datetime(2000,1,1),datetime(2000,1,31),False),
                        (0,"kWh",electricity,datetime(2000,1,1),datetime(2000,1,31))])
def consumption_zero_one_month(request):
    return Consumption(*request.param)

@pytest.fixture(scope="session",params=[electricity,natural_gas,propane,FuelType("fuel_oil")])
def fuel_type(request):
    return request.param

@pytest.fixture
def consumption_list_one_year_electricity():
    return [Consumption(1000,"kWh",electricity,datetime(2012,1,1),datetime(2012,2,1)),
            Consumption(1100,"kWh",electricity,datetime(2012,2,1),datetime(2012,3,1)),
            Consumption(1200,"kWh",electricity,datetime(2012,3,1),datetime(2012,4,1)),
            Consumption(1300,"kWh",electricity,datetime(2012,4,1),datetime(2012,5,1)),
            Consumption(1400,"kWh",electricity,datetime(2012,5,1),datetime(2012,6,1)),
            Consumption(1500,"kWh",electricity,datetime(2012,6,1),datetime(2012,7,1)),
            Consumption(1400,"kWh",electricity,datetime(2012,7,1),datetime(2012,8,1)),
            Consumption(1300,"kWh",electricity,datetime(2012,8,1),datetime(2012,9,1)),
            Consumption(1200,"kWh",electricity,datetime(2012,9,1),datetime(2012,10,1)),
            Consumption(1100,"kWh",electricity,datetime(2012,10,1),datetime(2012,11,1)),
            Consumption(1000,"kWh",electricity,datetime(2012,11,1),datetime(2012,12,1)),
            Consumption(900,"kWh",electricity,datetime(2012,12,1),datetime(2013,1,1))]

@pytest.fixture
def consumption_list_one_year_gas():
    return [Consumption(900,"thm",natural_gas,datetime(2012,1,1),datetime(2012,2,1)),
            Consumption(950,"thm",natural_gas,datetime(2012,2,1),datetime(2012,3,1)),
            Consumption(800,"kWh",natural_gas,datetime(2012,3,1),datetime(2012,4,1)),
            Consumption(700,"kWh",natural_gas,datetime(2012,4,1),datetime(2012,5,1)),
            Consumption(500,"kWh",natural_gas,datetime(2012,5,1),datetime(2012,6,1)),
            Consumption(100,"kWh",natural_gas,datetime(2012,6,1),datetime(2012,7,1)),
            Consumption(100,"kWh",natural_gas,datetime(2012,7,1),datetime(2012,8,1)),
            Consumption(100,"kWh",natural_gas,datetime(2012,8,1),datetime(2012,9,1)),
            Consumption(200,"kWh",natural_gas,datetime(2012,9,1),datetime(2012,10,1)),
            Consumption(400,"kWh",natural_gas,datetime(2012,10,1),datetime(2012,11,1)),
            Consumption(700,"kWh",natural_gas,datetime(2012,11,1),datetime(2012,12,1)),
            Consumption(900,"kWh",natural_gas,datetime(2012,12,1),datetime(2013,1,1))]

##### Test cases #####

def test_consumption_has_correct_attributes(consumption_zero_one_month):
    assert consumption_zero_one_month.joules == 0
    assert isinstance(consumption_zero_one_month.fuel_type,FuelType)
    assert consumption_zero_one_month.start == datetime(2000,1,1)
    assert consumption_zero_one_month.end == datetime(2000,1,31)
    assert consumption_zero_one_month.estimated == False

def test_fuel_type(fuel_type):
    assert fuel_type.name == str(fuel_type)
    assert isinstance(fuel_type,FuelType)

def test_automatic_unit_conversion():
    btu_consumption = Consumption(1,"Btu",electricity,datetime(2000,1,1),datetime(2000,1,31),False)
    kwh_consumption = Consumption(1,"kWh",electricity,datetime(2000,1,1),datetime(2000,1,31),False)
    therm_consumption = Consumption(1,"therm",electricity,datetime(2000,1,1),datetime(2000,1,31),False)
    assert abs(1 - btu_consumption.btu) < EPSILON
    assert abs(1 - btu_consumption.BTU) < EPSILON
    assert abs(1 - btu_consumption.BTUs) < EPSILON
    assert abs(1 - btu_consumption.to("btu")) < EPSILON
    assert abs(1 - kwh_consumption.kWh) < EPSILON
    assert abs(1 - kwh_consumption.kilowatthour) < EPSILON
    assert abs(1 - kwh_consumption.kilowatthours) < EPSILON
    assert abs(1 - therm_consumption.thm) < EPSILON
    assert abs(1 - therm_consumption.therm) < EPSILON
    assert abs(1 - therm_consumption.therms) < EPSILON
    assert abs(therm_consumption.joules - btu_consumption.joules * 100000) < EPSILON
    with pytest.raises(UndefinedUnitError):
        assert abs(1 - kwh_consumption.kwh) < EPSILON

def test_feasible_consumption_start_end():
    with pytest.raises(DateRangeException):
        Consumption(1,"Btu",electricity,datetime(2000,1,2),datetime(2000,1,1))

def test_consumption_invalid_fuel_type():
    with pytest.raises(InvalidFuelTypeException):
        Consumption(1,"Btu","Invalid",datetime(2000,1,1),datetime(2000,1,31))

def test_timedelta(consumption_zero_one_month):
    delta = consumption_zero_one_month.timedelta
    assert delta.days == 30

def test_consumption_has_representation(consumption_zero_one_month):
    assert "Consumption" in consumption_zero_one_month.__repr__()

def test_consumption_history(consumption_list_one_year_electricity,
        consumption_list_one_year_gas):
    ch_elec = ConsumptionHistory(consumption_list_one_year_electricity)
    ch_gas = ConsumptionHistory(consumption_list_one_year_gas)
    assert len(ch_elec.electricity) == 12
    assert len(ch_elec.natural_gas) == 0
    assert len(ch_gas.electricity) == 0
    assert len(ch_gas.natural_gas) == 12
    for consumption in ch_elec.electricity:
        assert consumption.kWh >= 0
    for consumption in ch_gas.natural_gas:
        assert consumption.therm >= 0
    assert len(ch_elec.get(electricity)) == 12

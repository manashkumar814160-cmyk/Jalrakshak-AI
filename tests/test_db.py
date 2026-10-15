import pytest
from core.db import *
def test_farm_crud_and_validation():
    init_db(); f={"name":"A","place":"Hyderabad","latitude":17,"longitude":78,"crop":"Tomato","soil":"Loamy","irrigation_method":"Drip","area_acres":1,"sowing_date":"2026-01-01"}; i=save_farm(f); assert get_farm(i)["name"]=="A"; delete_farm(i); assert get_farm(i) is None
def test_invalid_area_and_harvest_date_rejected():
    init_db(); f={"name":"A","place":"Hyderabad","latitude":17,"longitude":78,"crop":"Tomato","soil":"Loamy","irrigation_method":"Drip","area_acres":1,"sowing_date":"2026-02-01","harvest_date":"2026-01-01"}
    with pytest.raises(ValueError): save_farm(f)

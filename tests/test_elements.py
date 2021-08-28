def test_diffusivity(water):
    assert water.thermal_diffusivity == (water.thermal_conductivity
                                         / water.specific_heat_capacity)

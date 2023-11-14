import numpy as np
import pandas as pd

def capacity_calc(dwt:int, ship_type:str)->int:
    """calculate the capcity for calculating EEDI

    Args:
        dwt (int): deadweight of the ship in tonnes
        ship_type (str): type of ship

    Returns:
        int: deadweight used in EEDI calculation
    """ 
    if ship_type != 'container_ship':
        output = dwt
    else:
        output = dwt * 0.7
    return output

def fuel_ratio(
    v_mdo:float, v_lfo:float, v_hfo:float, v_lng:float,
    power_mdo:int, power_lfo:int, power_hfo:int, power_lng:int,
    rho_mdo:float=900, rho_lfo:float=980,
    rho_hfo:float=991, rho_lng:float=450,
    lcv_mdo:float=42700, lcv_lfo:float=41200,
    lcv_hfo:float=40200, lcv_lng:float=48000,
    k_mdo:float=0.98, k_lfo:float=0.98,
    k_hfo:float=0.98, k_lng:float=0.95)->float:
    """Function to calculate primary fuel

    Args:
        v_mdo (float): Total fuel capacity of MDO in cubic Metres
        v_lfo (float): Total fuel capacity of LFO in cubic Metres
        v_hfo (float): Total fuel capacity of HFO in cubic Metres
        v_lng (float): Total fuel capacity of lng in cubic Metres
        power_mdo (int): Total installed power of main and aux MDO
            engines
        power_lfo (int): Total installed power of main and aux LFO
            engines
        power_hfo (int): Total installed power of main and aux HFO
            engines
        power_lng (int): Total installed power of main and aux LNG
            engines
        rho_mdo (float, optional): Density of MDO in Kilograms per
            cubic Metres. Defaults to 900.
        rho_lfo (float, optional): Density of LFO in Kilograms per
            cubic Metres. Defaults to 980.
        rho_hfo (float, optional): Density of HFO in Kilograms per
            cubic Metres. Defaults to 991.
        rho_lng (float, optional): Density of lng in Kilograms per
            cubic Metres. Defaults to 450.
        lcv_mdo (float, optional): Lower calorific value of MDO in
            Kilojoules per Kilogram. Defaults to 42700.
        lcv_lfo (float, optional): Lower calorific value of LFO in
            Kilojoules per Kilogram. Defaults to 41200.
        lcv_hfo (float, optional): Lower calorific value of HFO in
            Kilojoules per Kilogram. Defaults to 40200.
        lcv_lng (float, optional): Lower calorific value of LNG in
            Kilojoules per Kilogram. Defaults to 48000.
        k_mdo (float, optional): Filling rate of MDO (max fill % of
            the fuel tank). Defaults to 0.98.
        k_lfo (float, optional): Filling rate of LFO (max fill % of
            the fuel tank). Defaults to 0.98.
        k_hfo (float, optional): Filling rate of HFO (max fill % of
            the fuel tank). Defaults to 0.98.
        k_lng (float, optional): Filling rate of lng (max fill % of
            the fuel tank). Defaults to 0.95.

    Returns:
        float: gas fuel ratio, liquid fuel ratio
    """
    if (power_lng > 0) & (v_lng > 0):
        power_ratio = (power_mdo + power_lfo 
                       + power_hfo + power_lng) / power_lng
        gas = v_lng * rho_lng * lcv_lng * k_lng
        mdo = v_mdo * rho_mdo * lcv_mdo * k_mdo
        lfo = v_lfo * rho_lfo * lcv_lfo * k_lfo
        hfo = v_hfo * rho_hfo * lcv_hfo * k_hfo
        
        output = power_ratio * (gas / (mdo + lfo + hfo + gas))
    else:
        output = 0    
    
    return output

def main_engine_power(me_power:int,
                      me_type:str,
                      pto_dediction:int=0,
                      electrical_eff:float=0.913)->int:
    """Function to calculate Pme

    Args:
        me_power (int): power of main engine in kW
        me_type (str): choose either 'diesel'
            'dual_fuel'
            'steam_turbine'
            'diesel_electric'
        pto_dediction (int): corrections applied for pto in kW
        electrical_eff (float, optional): only used for diesel_electric.
            total electrical efficiency, see above. Defaults to 0.913.

    Returns:
        int: Pme - main engine power for the EEDI calculation
    """    
    if (me_type == 'diesel') or (me_type == 'dual_fuel'):
        me_75 = me_power * 0.75
    elif me_type == 'steam_turbine':
        me_75 = me_power * 0.83
    elif me_type == 'diesel_electric':
        me_75 = (me_power * 0.83) / electrical_eff
        
    output = me_75 - pto_dediction
    
    return output

def shaft_gen_reduc_to_me(pae:float,
                    p_pto:int,
                    me_type:str)->float:
    """Calculate shaft generator reduction to Pme

    Args
        pae (float): total auxiliary power load in kW
        p_pto (int): sum of the rated electrical output of all PTOs in
            Kilowatts.
        me_type (str): choose either 'diesel'
            'dual_fuel'
            'steam_turbine'
            'diesel_electric'
    
    It is assumed the calculation for DE propulsion is the same as traditional
    propulsion
    
    Returns:
        float: shaft generator reduction to be subtracted from Pme
    """ 
    reduction = min(pae / 0.75, p_pto * 0.75) #pto output at 75%
    
    standard_list = ['diesel', 'dual_fuel', 'diesel_electric']
    if me_type in standard_list:
        output = reduction * 0.75
    elif me_type == 'steam_turbine':
        output = reduction * 0.83
    
    return output

def p_pto_calc(p_pto_rated:int,
               me_type:str)->float:
    """Calculate shaft generator power P_pto

    Args
        p_pto_rated (int): sum of the rated electrical output of all PTOs in
            Kilowatts.
        me_type (str): choose either 'diesel'
            'dual_fuel'
            'steam_turbine'
            'diesel_electric'
    
    It is assumed the calculation for DE propulsion is the same as traditional
    propulsion
    
    Returns:
        float: shaft generator power P_pto
    """
    standard_list = ['diesel', 'dual_fuel', 'diesel_electric']
    if me_type in standard_list:
        output = p_pto_rated * 0.75
    elif me_type == 'steam_turbine':
        output = p_pto_rated * 0.83
        
    return output

def shaft_motor_power(p_sm_rated:int,
                      me_type:str,
                      gen_efficiency:float=0.93,
                      pti_eff:float=0.97)->float:
    """Calculate shaft motor increase to Pme

    Args:
        p_sm_rated (int): sum of the rated power consumption of all all shaft
             motors in Kilowatts
        me_type (str): choose either 'diesel'
            'dual_fuel'
            'steam_turbine'
            'diesel_electric'
        gen_efficiency (float, optional): weighted efficiency of the generators
            to provide power to the shaft motors. Defaults to 0.93.
        pti_eff (float, optional): efficiency of the shaft motors.
            Defaults to 0.97.

    Returns:
        float: shaft motor correction applied to be added to Pme
    """
    
    standard_list = ['diesel', 'dual_fuel', 'diesel_electric']
    if me_type in standard_list:
        p_pti = (p_sm_rated * 0.75) / gen_efficiency
        p_pti_shaft = p_sm_rated * pti_eff * 0.75
    elif me_type == 'steam_turbine':
        p_pti = (p_sm_rated * 0.83) / gen_efficiency
        p_pti_shaft = p_sm_rated * pti_eff * 0.75
    # p_pti = (
    #     ((me_type in standard_list)
    #      * (0.75 * p_sm_rated) / gen_efficiency)
    #     + ((me_type == 'steam_turbine')
    #        * (0.83 * p_sm_rated) / gen_efficiency)
    #     )        
    # p_pti_shaft = (
    #     (((me_type in standard_list)
    #       * (0.75 * p_sm_rated * pti_eff))
    #     + ((me_type == 'steam_turbine')
    #        * (0.83 * p_sm_rated * pti_eff)))
    # )
    return p_pti, p_pti_shaft

def reliqu_addition(cube:int, bor:float,
                    cop_cooling:float=0.166, r_reliq:float=1)->float:
    """calculate additional auxiliary load for reliquefaction system

    Args:
        cube (int): gas tank capacity in cubic Metres
        bor (float): design rate of boil-off gas of entire ship per day
        cop_cooling (float): coefficient of design performance of reliquefaction system
        r_reliq (float): ratio of boil-off gas (BOG) to be reliquefied to entire BOG

    Returns:
        float: Additional auxiliary power load in kW from reliquefaction system
    """    
    cop_reliq = (
        (425 * 511)
        / (24 * 3600 * cop_cooling)) #see MEPC.364(79) 2.2.5.6.3 for more info
    output = cube * bor * cop_reliq * r_reliq
    return output

def fuel_compressor(ship_type:str,
                    me_engine_stroke:str,
                    sfc_me_gas_mode:int,
                    p_me:int,
                    cop_comp:int=0.33)->float:
    """calculate additional auxiliary load for fuel compressor

    Args:
        ship_type (str): type of ship from pre-defined list
        me_engine_stroke (str): type of main engine. options are
            'two_stroke' or 'four_stroke'
        sfc_me_gas_mode (int): specific fuel consumption of main engine in gas mode in g/kWhr
        p_me (int): main engine power for the EEDI calculation in kW            
        cop_comp (int, optional): design power performance of compressors in kWhr/kg. Defaults to 0.33.

    Returns:
        float: Additional auxiliary power load in kW from high pressure fuel compressors
    """
    if ship_type == 'lng_carrier':
        if me_engine_stroke == 'two_stroke':
            output = (p_me / 1000) * cop_comp * sfc_me_gas_mode
        elif me_engine_stroke == 'four_stroke':
            output = p_me * 0.02
    else:
        output = 0
    # output = (
    #     (ship_type == 'lng_carrier')
    #     * (((me_engine_stroke == 'two_stroke')
    #     * cop_comp * sfc_me_gas_mode * (p_me / 1000))
    #     + ((me_engine_stroke == 'four_stroke')
    #     * 0.02 * p_me))
    #           )
    return output

def calc_pae(mcr_me:float,
             p_pti:float=0)->float:
    """calculate auxiliary power load in kW

    Args:
        mcr_me (float): sum of maximum continuous rating of all main engines in kW
        p_pti (float, optional): power of shaft motors (if used) in kW. Defaults to 0.

    Returns:
        float: auxlilary power load in kW. This does not include additions to the auxlilary power such as reliquefaction systems
    """    
    limit = mcr_me + (p_pti / 0.75)
    if limit >= 10000:
        output = (limit * 0.025) + 250
    elif limit < 10000:
        output = limit * 0.05
    # output  = (
    #     ((limit >= 10000)
    #      * ((0.025 * limit)+250))
    #     + ((limit < 10000)
    #      * (0.05 * limit))
    # )
    return output

def p_ae_iterative_calc(ship_type:str,
              me_type:str,
              me_engine_stroke:str,
              installed_power:float,
              add_load:float=0,
              p_pto_rated:float=0,
              p_sm_rated:float=0,  
              sfc_me_gas_mode:float=0,            
              cube:float=0,
              bor:float=0)->float:
    """calculate ae power

    Args:
        ship_type (str): ship type
        me_type (str): choose either 'diesel'
            'dual_fuel'
            'steam_turbine'
            'diesel_electric'
        me_engine_stroke (str): type of main engine. options are
            'two_stroke' or 'four_stroke'
        installed_power (float): total ME installed power in kW
        add_load (float): additional auxiliary load in kW. Defaults to 0.
        p_pto_rated (float, optional): p_pto_rated (float): sum of the rated electrical
        output of all PTOs in Kilowatts. Defaults to 0.
        p_sm_rated (float, optional): sum of the rated power consumption of all
        all shaft motors in Kilowatts. Defaults to 0.
        sfc_main_engine_gas_mode (float): weighted sfc of me in gas mode in g/kWh.
            Defaults to 0
        cube (float, optional): gas tank capacity in cubic Metres.
            Defaults to 0.
        bor (float, optional): design rate of boil-off gas of entire ship
            per day. Defaults to 0.

    Returns:
        float: ae power with additional ae loads such as reliq system
    """    
    
    # This is an interative loop when an lng carrier with compressors for high
    # pressure gas fuel. If not applicable, the loop still runs but no change
    # between iterations occur
    
    # Initiate loop
    pme = main_engine_power(me_power = installed_power,
                            me_type = me_type)


    for i in range(5):
        #calculate compressor power for high pressure gas fuel supply
        compressors = fuel_compressor(ship_type = ship_type,
                                    me_engine_stroke = me_engine_stroke,
                                    sfc_me_gas_mode = sfc_me_gas_mode,
                                    p_me = pme)
        
        #calculate reliquefaction plant power
        reliq = reliqu_addition(cube = cube,
                                bor = bor)
        
        #calculate shaft motor power (can be equal to 0)
        p_sm = shaft_motor_power(p_sm_rated = p_sm_rated,
                                me_type = me_type)[0]
        
        #calculate pae
        pae = calc_pae(mcr_me = installed_power,
                    p_pti = p_sm) + compressors + reliq + add_load
        
        #calculate reduction to pme from shaft generator
        shaft_gen_reduct_to_me_kw = shaft_gen_reduc_to_me(pae=pae,
                            p_pto=p_pto_rated,
                            me_type=me_type)
        
        #calculate pme
        pme = main_engine_power(me_power = installed_power,
                                me_type = me_type,
                                pto_dediction=shaft_gen_reduct_to_me_kw)
                
    return pae

def ice_class_correction(ship_type:str,
                         ice_class:str,
                         mcr:float,
                         dwt:float)->float:
    """calculate ice-class correction

    Args:
        ship_type (str): ship type. Should be one of:
            tanker
            bulk_carrier
            general_cargo
            refrigerated_cargo
        ice_class (str): ice class. Should be one of:
            'none'
            'ia_super'
            'ia'
            'ib'
            'ic'
        mcr (float): sum of maximum continuous rating
            of main engines in kW
        dwt (float): deadweight tonnes of ship in tonnes

    Returns:
        float: ice class power correction factore, fj 
    """
    #initiate variables if statements are false
    fj_0 = 1
    fj_min = 1
    
    if ship_type == 'tanker':
        fj_0 = (17.444 * dwt ** 0.5766) / mcr
        if ice_class == 'ia_super':
            fj_min = 0.2488 * dwt ** 0.0903
        elif ice_class == 'ia':
            fj_min = 0.4541 * dwt ** 0.0524
        elif ice_class == 'ib':
            fj_min = 0.7783 * dwt ** 0.0145
        elif ice_class == 'ic':
            fj_min = 0.8741 * dwt ** 0.0079
        else:
            fj_min = 1
            
    elif ship_type == 'bulk_carrier':
        fj_0 = (17.207 * dwt ** 0.5705) / mcr
        if ice_class == 'ia_super':
            fj_min = 0.2515 * dwt ** 0.0851
        elif ice_class == 'ia':
            fj_min = 0.3918 * dwt ** 0.0556
        elif ice_class == 'ib':
            fj_min = 0.8075 * dwt ** 0.0071
        elif ice_class == 'ic':
            fj_min = 0.8573 * dwt ** 0.0087
        else:
            fj_min = 1
            
    elif ship_type == 'general_cargo':
        fj_0 = (1.974 * dwt ** 0.7987) / mcr
        if ice_class == 'ia_super':
            fj_min = 0.1381 * dwt ** 0.1435
        elif ice_class == 'ia':
            fj_min = 0.1574 * dwt ** 0.1440
        elif ice_class == 'ib':
            fj_min = 0.3256 * dwt ** 0.0922
        elif ice_class == 'ic':
            fj_min = 0.4966 * dwt ** 0.0583
        else:
            fj_min = 1
            
    elif ship_type == 'refrigerated_cargo':
        fj_0 = (5.598 * dwt ** 0.696) / mcr
        if ice_class == 'ia_super':
            fj_min = 0.5254 * dwt ** 0.0357
        elif ice_class == 'ia':
            fj_min = 0.6325 * dwt ** 0.0278
        elif ice_class == 'ib':
            fj_min = 0.7670 * dwt ** 0.0159
        elif ice_class == 'ic':
            fj_min = 0.8918 * dwt ** 0.0079
        else:
            fj_min = 1
    
    else:
        fj_0 = 1
       
    # fj_0 = (
    #     ((ship_type == 'tanker')
    #     * (17.444 * dwt ** 0.5766) / mcr
    #     )
    #     + ((ship_type == 'bulk_carrier')
    #     * (17.207 * dwt ** 0.5705) / mcr
    #     )
    #     + ((ship_type == 'general_cargo')
    #     * (1.974 * dwt ** 0.7987) / mcr
    #     )
    #     + ((ship_type == 'refrigerated_cargo')
    #     * (5.598 * dwt ** 0.696) / mcr
    #     )
    # )
    
    # fj_min = (
    #     # tanker
    #     ((ship_type == 'tanker')
    #      * (
    #          ((ice_class == 'ia_super')
    #           * (0.2488 * dwt ** 0.0903))
    #          +((ice_class == 'ia')
    #            * (0.4541 * dwt ** 0.0524))
    #          +((ice_class == 'ib')
    #            * (0.7783 * dwt ** 0.0145))
    #          +((ice_class == 'ic')
    #            * (0.8741 * dwt ** 0.0079))
    #          ))
    #     # bulk carrier
    #     + ((ship_type == 'bulk_carrier')
    #      * (
    #          ((ice_class == 'ia_super')
    #           * (0.2515 * dwt ** 0.0851))
    #          +((ice_class == 'ia')
    #            * (0.3918 * dwt ** 0.0556))
    #          +((ice_class == 'ib')
    #            * (0.8075 * dwt ** 0.0071))
    #          +((ice_class == 'ic')
    #            * (0.8573 * dwt ** 0.0087))
    #          ))
    #     # general cargo
    #     + ((ship_type == 'general_cargo')
    #      * (
    #          ((ice_class == 'ia_super')
    #           * (0.1381 * dwt ** 0.1435))
    #          +((ice_class == 'ia')
    #            * (0.1574 * dwt ** 0.1440))
    #          +((ice_class == 'ib')
    #            * (0.3256 * dwt ** 0.0922))
    #          +((ice_class == 'ic')
    #            * (0.4966 * dwt ** 0.0583))
    #          ))
    #     # refrigerated_cargo
    #     + ((ship_type == 'refrigerated_cargo')
    #      * (
    #          ((ice_class == 'ia_super')
    #           * (0.5254 * dwt ** 0.0357))
    #          +((ice_class == 'ia')
    #            * (0.6325 * dwt ** 0.0278))
    #          +((ice_class == 'ib')
    #            * (0.7670 * dwt ** 0.0159))
    #          +((ice_class == 'ic')
    #            * (0.8918 * dwt ** 0.0079))
    #          ))
    # )
    
    output = min(max(fj_0, fj_min),1)
    return output

def shuttle_correction(ship_type:str,
                       dwt:float,
                       propulsion_redundancy:bool)->float:
    """calculate shuttle tanker correction

    Args:
        ship_type (str): ship type
        dwt (float): deadweight tonnes of ship
        in tonnes
        propulsion_redundancy (bool): does the
            ship have propulsion redundancy?
            True == yes
            False == no

    Returns:
        float: shuttle tanker power correction factore, fj 
    """
    criteria = ((ship_type == 'shuttle_tanker')
                and (propulsion_redundancy == True)
                and (dwt >= 80000)
                and (dwt <= 160000))
    if criteria == True:
        output = 0.77
    else:
        output = 1.
    
    return output

def roro_correction(ship_type:str,
                    l:float,
                    b:float,
                    d:float,
                    disp_m3:float,
                    v_ref:float,
                    g:float=9.81)->float:
    """calculate roro correction

    Args:
        ship_type (str): ship type
        l (float): length between perpendiculars in m
        b (float): beam in m
        d (float): draught in m
        disp_m3 (float): displacement in m^3
        v_ref (float): reference velocity in knots
        g (float, optional): acceleration due to gravity.
            Defaults to 9.81.

    Returns:
        float: roro cargo and roro passenger power
            correction factor, fj
    """      
    
    #initiate constants
    #_c denotes roro Cargo ship
    alpha_c = 2.
    beta_c = 0.5
    gamma_c = 0.75
    delta_c = 1.
    
    #_p denotes roro Passenger ship
    alpha_p = 2.5
    beta_p = 0.75
    gamma_p = 0.75
    delta_p = 1.
    
    fn = (0.5144 * v_ref) / ((l * g)**0.5)
    
    if ship_type == 'roro_cargo':
        fj_calc = (1
                   / ((fn ** alpha_c)
                      * ((l / b) ** beta_c)
                      * ((b / d) ** gamma_c)
                      * ((l / disp_m3 ** (1 / 3)) ** delta_c)))
    elif ship_type == 'roro_passenger':
        fj_calc = (1
                   / ((fn ** alpha_p)
                      * ((l / b) ** beta_p)
                      * ((b / d) ** gamma_p)
                      * ((l / disp_m3 ** (1 / 3)) ** delta_p)))
    else:
        fj_calc = 1.
        
    # fj_calc = (((ship_type == 'roro_cargo')
    #       * (1
    #          / (
    #              (fn ** alpha_c)
    #              * ((l / b) ** beta_c)
    #              * ((b / d) ** gamma_c)
    #              * ((l / disp_m3 ** (1 / 3)) ** delta_c))))
    #       + ((ship_type == 'roro_passenger')
    #       * (1
    #          / (
    #              (fn ** alpha_p)
    #              * ((l / b) ** beta_p)
    #              * ((b / d) ** gamma_p)
    #              * ((l / disp_m3 ** (1 / 3)) ** delta_p))))
    # )
    output = min(fj_calc, 1)
    return output

def general_cargo_correction(ship_type:str,
                             l:float,
                             b:float,
                             d:float,
                             disp_m3:float,
                             v_ref:float,
                             g:float=9.81)->float:
    """calcualte general cargo ship correction 

    Args:
        ship_type (str): ship type
        l (float): length between perpendiculars in m
        b (float): beam in m
        d (float): draught in m
        disp_m3 (float): displacement in m^3
        v_ref (float): reference velocity in knots
        g (float, optional): acceleration due to gravity.
            Defaults to 9.81.

    Returns:
        float: general cargo ship power
            correction factor, fj
    """
    if ship_type == 'general_cargo':
        #calculate constants
        fn_disp_calc = ((0.5144 * v_ref)
                        / (g * disp_m3 ** (1 / 3)) ** 0.5 )    
        fn_disp = min(fn_disp_calc, 0.6)        
        cb = disp_m3 / (l * b * d)
        #calculate fj
        fj_calc = 0.174 / (fn_disp ** 2.3 * cb ** 0.3)
    else:
        fj_calc = 1.
    
    # fj_calc = ((ship_type == 'general_cargo') 
    #        * (0.174 / (fn_disp ** 2.3 * cb ** 0.3)))
    
    output = min(fj_calc, 1)
    
    return output

def fj(ship_type:str,
       ice_class:str='none',
       mcr:float=0,
       dwt:float=0,
       propulsion_redundancy:bool=False,
       l:float=0,
       b:float=0,
       d:float=0,
       disp_m3:float=0,
       v_ref:float=0,
       g:float=9.81)->float:
    """calculate fj

    Args:
        ship_type (str): ship type
        ice_class (str, optional): ice class. Should be one of:
            'none'
            'ia_super'
            'ia'
            'ib'
            'ic'. Defaults to 'none'.
        mcr (float, optional): sum of maximum continuous rating
            of main engines in kW. Defaults to 0.
        dwt (float, optional): deadweight tonnes of ship in 
            tonnes. Defaults to 0.
        propulsion_redundancy (bool, optional): does the
            ship have propulsion redundancy?
            True == yes
            Flase == no. Defaults to False.
        l (float, optional): length between perpendiculars in m.
            Defaults to 0.
        b (float, optional): beam in m. Defaults to 0.
        d (float, optional): draught in m. Defaults to 0.
        disp_m3 (float, optional): displacement in m^3. Defaults to 0.
        v_ref (float, optional): reference velocity in knots.
            Defaults to 0.
        g (float, optional): acceleration due to gravity.
            Defaults to 9.81.

    Returns:
        float: value for fj - ship-specific design elements
    """
    ice_test = (ship_type in ['tanker','bulk_carrier','general_cargo','refrigerated_cargo']
                and ice_class in ['ia_super', 'ia', 'ib', 'ic']
                and all([v > 0 for v in [mcr, dwt]]))
    shut_redun_test = ((ship_type == 'shuttle_tanker') 
                       and (propulsion_redundancy == True)
                       and 80000 <= dwt <= 160000)
    test_vars = [l, b, d, disp_m3, v_ref]
    roro_test = (ship_type in ['roro_cargo', 'roro_passenger']
                 and all([v > 0 for v in test_vars]))
    genal_cargo_test = (ship_type == 'general_cargo'
                        and all([v > 0 for v in test_vars]))
            
    if ice_test == True:
        output = ice_class_correction(
            ship_type = ship_type,
            ice_class = ice_class,
            mcr = mcr,
            dwt = dwt)
        
    elif shut_redun_test == True:
        output = shuttle_correction(
            ship_type = ship_type,
            dwt = dwt,
            propulsion_redundancy = propulsion_redundancy)
        
    elif roro_test == True:
        output = roro_correction(
            ship_type = ship_type,
            l = l,
            b = b,
            d = d,
            disp_m3 = disp_m3,
            v_ref = v_ref,
            g = g)
        
    elif genal_cargo_test == True:
        output = general_cargo_correction(
            ship_type = ship_type,
            l = l,
            b = b,
            d = d,
            disp_m3 = disp_m3,
            v_ref = v_ref,
            g = g)
    
    else:
        output = 1
               
    return output

def ice_capacity_correction(ship_type:str,
                            ice_class:str,
                            dwt:float,
                            l:float,
                            b:float,
                            d:float,
                            disp_m3:float)->float:
    """calcualte capacity correction for ice-classed ships

    Args:
        ship_type (str): ship type
        ice_class (str): ship ice class
        dwt (float): deadweight capcity in tonnes
        l (float): length between perpendiculars in m
        b (float): beam in m
        d (float): draught in m
        disp_m3 (float): displacement in m^3

    Returns:
        float: capacity correction factor, fi
    """
    if ice_class == 'ia_super':
        fi_ice_class = 1.0151 +  228.7 / dwt
    elif ice_class == 'ia':
        fi_ice_class = 1.0099 +  95.1 / dwt
    elif ice_class == 'ib':
        fi_ice_class = 1.0067 +  62.7 / dwt
    elif ice_class == 'ic':
        fi_ice_class = 1.0041 +  58.5 / dwt
    else:
        fi_ice_class = 1.
        
    # fi_ice_class = (
    #     ((ice_class == 'ic')
    #      * 1.0041 +  58.5 / dwt)
    #     + ((ice_class == 'ib')
    #        * 1.0067 +  62.7 / dwt)
    #     + ((ice_class == 'ia')
    #        * 1.0099 +  95.1 / dwt)
    #     + ((ice_class == 'ia_super')
    #        * 1.0151 +  228.7 / dwt))
    
    if ship_type == 'bulker':
        if dwt < 10000:
            cb_ref = 0.78
        elif (dwt >= 10000) and (dwt < 25000):
            cb_ref = 0.8
        elif (dwt >= 25000) and (dwt < 55000):
            cb_ref = 0.82
        elif dwt >= 55000:
            cb_ref = 0.86
    
    elif ship_type == 'tanker':
        if dwt < 25000:
            cb_ref = 0.78
        elif (dwt >= 25000) and (dwt < 55000):
            cb_ref = 0.82
        elif dwt >= 55000:
            cb_ref = 0.83
    
    elif ship_type == 'general_cargo':
        cb_ref = 0.8
    
    else:
        cb_ref = 1
    
    
    if ship_type in {'bulk_carrier', 'tanker', 'general_cargo'}:
        fi_cb = cb_ref / (disp_m3 / (l * b * d))
    else:
        fi_cb = 1.
    # cb_ref = (
    #     ((ship_type == 'bulk_carrier')
    #      * (((dwt < 10000) * 0.78)
    #         + ((dwt >= 10000) * (dwt < 25000) * 0.8)
    #         + ((dwt >= 25000) * (dwt < 55000) * 0.82)
    #         + ((dwt >= 55000) * 0.86)))

        # + ((ship_type == 'tanker')
        #    * (((dwt < 25000) * 0.78)
        #       + ((dwt >= 25000) * (dwt < 55000) * 0.82)
        #       + ((dwt >= 55000) * 0.83)))
        
    #     + ((ship_type == 'general_cargo') * 0.8)
    # )
    
    # fi_cb = ((ship_type in {'bulk_carrier', 'tanker', 'general_cargo'})
    #          * cb_ref / (disp_m3 / (l * b * d))
    #          + ((ship_type not in {'bulk_carrier', 'tanker', 'general_cargo'})
    #             * 1))
    
    output = fi_ice_class * fi_cb
    return output

def struct_enhance_corr(disp_t:float,
                        lwt_ref:float,
                        lwt_enhance:float)->float:
    """calculate structural enhancement correction

    Args:
        disp_t (float): displacement in tonnes
        lwt_ref (float): lightweight before enhancements
            in tonnes
        lwt_enhance (float): lightweight after enhancements
            in tonnes

    Returns:
        float: correction for voluntary structural
            enhancements, fi_vse
    """    
    dwt_ref = disp_t - lwt_ref
    dwt_enhance = disp_t - lwt_enhance
    
    fi_vse = dwt_ref / dwt_enhance
    
    return fi_vse

def csr_corr(lwt:float,
             dwt:float)->float:
    """calculate common structural rules (csr) correction

    Args:
        lwt (float): ship lightweight in tonnes
        dwt (float): ship deadweight in tonnes

    Returns:
        float: correction for ships under csr,
            fi_csr
    """   
    output = 1 + (0.08 * lwt / dwt)
    
    return output 

def fi(ship_type:str,
       csr:bool,
       calc_pref:str='none',
       ice_class:str='none',
       dwt:float=0,
       l:float=0,
       b:float=0,
       d:float=0,
       disp_m3:float=0,
       disp_t:float=0,
       lwt_ref:float=0,
       lwt_enhance:float=0,
       lwt_csr:float=0,
       dwt_csr:float=0)->float:
    """calcuate fi

    Args:
        ship_type (str): ship type
        csr (bool): is the ship under common structural rules (csr)?
        calc_pre (str, optional): calculation preference for ice classed ships
            options are to use functions:
            none = 'none'
            ice_capacity_correction = 'ice'
            struct_enhance_corr = 'struct'. Defaults to 'none'.
        ice_class (str, optional): ice class. Should be one of:
            'none'
            'ia_super'
            'ia'
            'ib'
            'ic'. Defaults to 'none'.
        dwt (float, optional): deadweight tonnes of ship in 
            tonnes. Defaults to 0.
        l (float, optional): length between perpendiculars in m.
            Defaults to 0.
        b (float, optional): beam in m. Defaults to 0.
        d (float, optional): draught in m. Defaults to 0.
        disp_m3 (float, optional): displacement in m^3. Defaults to 0.
        disp_t (float, optional): displacement in tonnes. Defaults to 0.
        lwt_ref (float, optional): lightweight before enhancements
            in tonnes. Defaults to 0.
        lwt_enhance (float, optional): lightweight after enhancements
            in tonnes. Defaults to 0.
        lwt_csr (float, optional): ship lightweight in tonnes. Defaults to 0.
        dwt_csr (float, optional): ship deadweight in tonnes. Defaults to 0.

    Returns:
        float: calculate fi - capacity factor for technical/regulatory limitation on capacity
    """
    ice_test = (ship_type in ['tanker','bulk_carrier','general_cargo']
                and csr == False
                and calc_pref == 'ice'
                and ice_class in ['ia_super', 'ia', 'ib', 'ic']
                and all([v > 0 for v in [l, b, d, disp_m3]]))
    struct_test = (calc_pref == 'struct'
                   and csr == False
                   and all([v > 0 for v in [
                       disp_t, lwt_ref, lwt_enhance
                   ]]))
    csr_test = (ship_type in ['bulk_carrier', 'tanker']
                and csr == True
                and all([v > 0 for v in [lwt_csr, dwt_csr]]))
    
    output = 1
    
    if ice_test == True:
        output = ice_capacity_correction(
            ship_type = ship_type,
            ice_class = ice_class,
            dwt = dwt,
            l = l,
            b = b,
            d = d,
            disp_m3 = disp_m3)
        
    elif struct_test == True:
        output = struct_enhance_corr(
            disp_t = disp_t,
            lwt_ref = lwt_ref,
            lwt_enhance = lwt_enhance)
        
    elif csr_test == True:
        output = csr_corr(
            lwt = lwt_csr,
            dwt = dwt_csr)
        
    return output

def chemical_tanker_corr(ship_type:str,
                         dwt:float,
                         cube:float)->float:
    """calculate correction for chemical tanker capacity

    Args:
        ship_type (str): ship type
        dwt (float): ship deadweight in tonnes
        cube (float): ship cargo capacity in m^3

    Returns:
        float: correction for chemical tanker capacity, fc
    """    
    
    r = dwt / cube
    
    if (ship_type == 'chemical_tanker') and (r < 0.98):
        output = r ** (-0.7) - 0.014
    else:
        output = 1
    # fc = (((ship_type == 'chemical_tanker')
    #       * ((r < 0.98) * (r ** (-0.7) - 0.014)
    #          + (r >= 0.98) * 1))
    #       + ((ship_type != 'chemical_tanker')
    #          * 1))
    
    return output

def gas_carrier_corr(ship_type:str,
                     diesel_direct_drive:bool,
                     marpol_annex:str,
                     dwt:float,
                     cube:float)->float:
    """calcualte correction for gas carrier capacity

    Args:
        ship_type (str): ship type
        diesel_direct_drive (bool): gas carrier with direct diesel
            driven propulsion system
        marpol_annex (str): MARPOL ANNEX VI definition
        dwt (float): ship deadweight in tonnes
        cube (float): ship cargo capacity in m^3

    Returns:
        float: correction for gas carriers, fc_lng
    """    
    r = dwt / cube
    fc_test = ((ship_type == 'gas_carrier') 
               and (diesel_direct_drive == True)
               and (marpol_annex == '2.2.14'))
    
    if fc_test == True:
        output = r ** -0.56
    else:
        output = 1.
    # fc_lng = (((ship_type == 'gas_carrier') 
    #            * (diesel_direct_drive == True)
    #            * (marpol_annex == '2.2.14'))
    #           * r ** (-0.56))
    
    # output = fc_lng + ((fc_lng == 0) * 1)
    
    return output

def roro_pass_corr(ship_type:str,
                   dwt:float,
                   gt:float)->float:
    """calculate correction for roro passenger ships

    Args:
        ship_type (str): ship type
        dwt (float): deadweight in tonnes
        gt (float): _gross tonnage in tonnes as defined by
            International Convention of Tonnage Measurements
                of Ships 1969, annex I, regulation 3

    Returns:
        float: correction for roro passenger ships, fc_ropax
    """    
    
    ratio = dwt / gt
    
    if (ship_type == 'roro_passenger') and (ratio < 0.25):
        output = (ratio / 0.25) ** -0.8
    else:
        output = 1.
    
    # fc_ropax = (((ship_type == 'roro_passenger') 
    #              * (ratio < 0.25)
    #              * (ratio / 0.25) ** (-0.8))
                
    #             + ((ratio >= 0.25) 
    #                * 1))
    
    # output = fc_ropax + ((fc_ropax == 0) * 1)
    
    return output

def light_bulk_corr(ship_type:str,
                    dwt:float,
                    cube:float)->float:
    """calculate correction for light bulk carriers

    Args:
        ship_type (str): ship type
        dwt (float): ship deadweight in tonnes
        cube (float): ship cargo capacity in m^3

    Returns:
        float: correction for bulk carriers designed for
            light cargoes, fc_bclc
    """    
    
    r = dwt / cube
    
    if (ship_type == 'bulk_carrier') and (r < 0.55):
        output = r ** -0.15
    else:
        output = 1.
    
    # fc_bclc = (((ship_type == 'bulk_carrier') 
    #             * (r < 0.55)
    #             * r ** (-0.15))
               
    #            + ((r >= 0.55) 
    #             * 1))
    
    # output = fc_bclc + ((fc_bclc == 0) * 1)
    
    return output

def fc(ship_type:str,
       dwt:float=0,
       cube:float=0,
       diesel_direct_drive:bool=False,
       marpol_annex:str='none',
       gt:float=0)->float:
    """calculate fc

    Args:
        ship_type (str): ship type
        dwt (float, optional): ship deadweight in tonnes. Defaults to 0.
        cube (float, optional): ship cargo capacity in m^3. Defaults to 0.
        diesel_direct_drive (bool, optional): gas carrier with direct diesel
            driven propulsion system. Defaults to False.
        marpol_annex (str, optional): MARPOL ANNEX VI definition.
            '2.2.14' will apply a correction
            '2.2.16' will not apply a correction Defaults to 'none'.
        gt (float, optional): gross tonnage in tonnes as defined by
            International Convention of Tonnage Measurements
                of Ships 1969, annex I, regulation 3. Defaults to 0.

    Returns:
        float: calculate fc - cubic capacity correction factor
    """
    
    chemical_test = (ship_type == 'chemical_tanker'
                     and all([v > 0 for v in [dwt, cube]]))
    gas_test = (ship_type in ['gas_carrier', 'lng_carrier']
                and diesel_direct_drive == True
                and marpol_annex == '2.2.14')
    roro_test = (ship_type == 'roro_passenger'
                 and all([v > 0 for v in [dwt, gt]]))
    bulk_test = (ship_type == 'bulk_carrier')
    
    output = 1
    
    if chemical_test == True:
        output = chemical_tanker_corr(
            ship_type = ship_type,
            dwt = dwt,
            cube = cube)
        
    elif gas_test == True:
        output = gas_carrier_corr(
            ship_type = ship_type,
            diesel_direct_drive = diesel_direct_drive,
            marpol_annex = marpol_annex,
            dwt = dwt,
            cube = cube)
        
    elif roro_test == True:
        output = roro_pass_corr(
            ship_type = ship_type,
            dwt = dwt,
            gt = gt)
        
    elif bulk_test == True:
        output = light_bulk_corr(
            ship_type = ship_type,
            dwt = dwt,
            cube = cube)
        
    return output

def fl(ship_type:str,
                    dwt_ref:float,                    
                    number_of_cranes:int=0,
                    swl_crane:float=0,
                    reach_crane:float=0,                    
                    side_loader_weight:float=0,
                    roro_weight:float=0)->float:
    """calculate correction for cargo-related gear

    Args:
        ship_type (str): ship type
        dwt_ref (float): dead wight without cargo gears in tonnes        
        number_of_cranes (int, optional): number of cranes.
            Defaults to 0.
        swl_crane (float, optional): safe working load of crane in
            tonnes. Defaults to 0.
        reach_crane (float, optional): reach of crane in m.
            Defaults to 0.
        side_loader_weight (float, optional): weight of side loader.
            Defaults to 0.
        roro_weight (float, optional): weight of roro ramp in tonnes.
            Defaults to 0.

    Returns:
        float: correction for cargo-related gear, fi
    """    
    
    crane_terms = [number_of_cranes, swl_crane, reach_crane]
    
    if all(i > 0 for i in crane_terms): #all crane terms are more than 0
        f_cranes = 1 + (number_of_cranes * (0.0519 * swl_crane * reach_crane + 32.11)) / dwt_ref
    else:
        f_cranes = 1
    
    #calculation below is based on "Ship-specific voluntary structural enhancement"
    if side_loader_weight > 0:
        f_sideloader = dwt_ref / (dwt_ref + side_loader_weight)
    else:
        f_sideloader = 1
    
    if roro_weight > 0:
        f_roro = dwt_ref / (dwt_ref + roro_weight)
    else:
        f_roro = 1
    
    if ship_type == 'general_cargo':
        fl = f_cranes * f_sideloader * f_roro
    else:
        fl = 1
    
    return fl

def fm(ice_class:str)->int:
    """correction for ia super and ia classed ships

    Args:
        ice_class (str): ice class notation. Valid inputs
            are 'ia_super' and 'ia'

    Returns:
        int: calculate fm for ice-classed ships
    """
    if (ice_class == 'ia_super') or (ice_class == 'ia'):
        output = 1.05
    else:
        output = 1
    # fm = (
    #     ((ice_class == 'ia_super') * 0.05)
    #     + ((ice_class == 'ia') * 0.05)
    #       ) + 1
    
    return output

def cat_b1(p_p_eff_al:float, p_ae_eff_al:float,
           p_me:float, p_pti_shaft:float,
           sfc_ae:float, cf_ae:float,
           sfc_me:float, cf_me:float)->float:
    """calculate effective power reduction of category b1 technology

    Args:
        p_p_eff_al (float): reduction in propulsion power at vref
            due to technology in kW
        p_ae_eff_al (float): increase in auxiliary power at vref
            due to technology in kW
        p_me (float): p_me for eedi calc in kW
        p_pti_shaft (float): pti power addition to shaft in kW
        sfc_ae (float): average specific fuel consumption of
            auxiliary engine
        cf_ae (float): average conversion factor for auxiliary
            engine (t-co2/t-fuel)
        sfc_me (float): average specific fuel consumption
            of main engine.
        cf_me (float): average conversion factor for main
            engine (t-co2/t-fuel).

    Assumed MEPC.1/Circ.896 has a typo in equation 1. *P_pti(i) is assumed
        to be P_pto
    Returns:
        float: calculate effective power reduction of category b1 technology
    """    
    cf_sfc_weighted = (((p_me * cf_me * sfc_me) + (p_pti_shaft * cf_ae * sfc_ae))
                       / (p_me + p_pti_shaft))
    
    p_eff = p_p_eff_al - p_ae_eff_al * ((cf_ae * sfc_ae) / cf_sfc_weighted)
             
    
    return p_eff, cf_sfc_weighted

def cat_b1_short(p_p_eff_al:float, p_ae_eff_al:float,
           p_me:float, p_pti_shaft:float,
           cf_sfc_me:float, cf_sfc_ae:float)->float:
    """calculate effective power reduction of category b1 technology

    Args:
        p_p_eff_al (float): reduction in propulsion power at vref
            due to technology in kW
        p_ae_eff_al (float): increase in auxiliary power at vref
            due to technology in kW
        p_me (float): p_me for eedi calc in kW
        p_pti_shaft (float): pti power addition to shaft in kW
        cf_sfc_me (float): cf_me x sfc_me weighted by the individual
            powers of the main engines 
        cf_sfc_ae (float): cf_me x sfc_ae weighted by the individual
            powers of the aux engines

    Assumed MEPC.1/Circ.896 has a typo in equation 1. *P_pti(i) is assumed
        to be P_pto
    Returns:
        float: calculate effective power reduction of category b1 technology
    """
     
    cf_sfc_weighted = (((p_me * cf_sfc_me) + (p_pti_shaft * cf_sfc_ae))
                       / (p_me + p_pti_shaft))
    
    p_eff = p_p_eff_al - p_ae_eff_al * ((cf_sfc_ae) / cf_sfc_weighted)
             
    
    return p_eff, cf_sfc_weighted

def cat_c1(w_e:float,
           eta_g:float,
           p_ae_eff_loss:float)->float:
    """calculate effective power reduction of category c1 technology 

    Args:
        w_e (float): calculated production of electricity by
            the waste heat recover system in kW
        eta_g (float): weighted average generator efficiency
        p_ae_eff_loss (float): pump power to drive the waste
            heat recovery system in kW

    Returns:
        float: calculate effective power reduction of category c1 technology
    """
    
    if (w_e > 0) & (eta_g > 0):
        p_ae_eff_dash = w_e / eta_g
    else:
        p_ae_eff_dash = 0
    p_ae_eff = p_ae_eff_dash - p_ae_eff_loss
    
    return p_ae_eff

def cat_c2(f_temp:float,
           p_max:float,
           etad_gen:float,
           n:int,
           f_rad:float=0.2,           
           l_others:float=10)->float:
    """calculate effective power reduction of category c2 technology

    Args:
        f_temp (float): tmperature coefficient specified by panel
            manufacturer in %/K
        p_max (float): nominal maximum generated PV power generation in kW
        etad_gen (float): weighted average efficiency of generators
        n (int): number of modules in the system
        f_rad (float, optional): ratio of average solar irradiance on main route
            to solar irradiance specified by the manufacturer. Defaults to 0.2.
        l_others (float, optional): summation of other losses including
            power conditioner, electrical resistance etc in %. Defaults to 10.

    Returns:
        float: calculate effective power reduction of category c2 technology
    """
    l_temp = f_temp * (40 - 25)
    f_eff = f_rad * (1 + l_temp / 100)
    if (n > 0) & (etad_gen > 0):
        p_ae_eff = p_max * (1 - l_others / 100) * n / etad_gen
    else:
        p_ae_eff = 0
    
    output = f_eff * p_ae_eff
    
    return output

def empty_series(x):
    if x.empty:
        out = 0
    else:
        out = sum(x)
    return out

def load_variables(inpt):
    #drop rows with me or ae terms. Keep only columns required for analysis
    df_inpt = inpt.iloc[:77].dropna(subset='ship parameters')
    df_inpt = df_inpt[['ship parameters', 'value']]

    #drop csv titles denoted with '#' at the start
    df_inpt = df_inpt[~df_inpt['ship parameters'].str.contains('#')].reset_index(drop=True)

    #create wide dataframe to set dtypes for each parameter
    df_inpt = df_inpt.set_index('ship parameters').T

    float_list = ['v_ref', 'dwt', 'lpp', 'b', 'ds', 'disp_m3',
                'p_pto_rated', 'p_sm_rated', 'speed_power_a',
                'speed_power_b', 'speed_power_c','v_lng', 'v_hfo',
                'v_mdo', 'v_lfo', 'k_lng', 'k_hfo', 'k_mdo', 
                'k_lfo', 'lwt_ref', 'lwt_enhance', 'lwt_csr',
                'dwt_csr', 'cube', 'gt', 'number_of_cranes',
                'swl_crane', 'reach_crane', 'side_loader_weight',
                'roro_weight', 'p_p_eff_al',
                'p_ae_eff_al', 'w_e', 'eta_g', 'p_ae_eff_loss',
                'f_temp', 'p_max', 'etad_gen', 'n']
    str_list = ['ship_type', 'propulsion_type', 'me_engine_stroke',
                'speed_power_equ', 'ice_class', 'marpol_annex']
    bool_list = ['propulsion_redundancy', 'csr', 'diesel_direct_drive']

    #set column dtypes
    df_inpt[float_list] = df_inpt[float_list].astype(float)
    df_inpt[str_list] = df_inpt[str_list].astype(object)
    df_inpt[bool_list] = df_inpt[bool_list].astype(bool)
    
    return df_inpt

def load_cf_dict(inpt):
    df_cf = inpt.iloc[102:].copy()
    df_cf.columns = df_cf.iloc[0]
    df_cf = df_cf[1:].reset_index(drop=True)
    df_cf.columns.name = None
    df_cf = df_cf[['fuel', 'lower_calorific_value', 'cf']]

    cf_dict = df_cf.set_index('fuel').T.to_dict('list')
    
    return cf_dict

def load_me_data(inpt, df_inpt):
    #initialise column dtypes
    int_vals_eng = ['engine_number']
    str_vals_eng = ['engine_type','liquid_fuel_type', 'pilot_fuel_type', 'gas_fuel_type']
    float_vals_eng = ['mcr', 'sfc_liquid_fuel', 'sfc_pilot_fuel', 'sfc_gas_fuel_kj']

    #create df_me df, rename columns and reset index
    df_me = inpt.iloc[79:89].copy()
    df_me.columns = df_me.iloc[0]
    df_me = df_me[1:].reset_index(drop=True)
    df_me.columns.name = None
    #transpose df_me to set column dtypes
    df_me = df_me.T.reset_index()
    df_me.columns = df_me.iloc[0]
    df_me = df_me[1:11].reset_index(drop=True)
    #set column dtypes
    df_me[int_vals_eng] = df_me[int_vals_eng].astype(int)
    df_me[str_vals_eng] = df_me[str_vals_eng].astype(object)
    df_me[float_vals_eng] = df_me[float_vals_eng].astype(float)

    df_me.dropna(subset='mcr', inplace=True)

    df_me['p_me'] = np.nan

    try: #calc when engine limitation is in place
        for i in df_me.loc[df_me['limited_power']>0].index:
            df_me.loc[i,'p_me'] = main_engine_power(me_power = df_me.loc[i,'limited_power'],
                                                    me_type = df_inpt['propulsion_type'].item())
    except:
        pass
    try: #calc when engine limitation is not in place
        for i in df_me.loc[df_me['limited_power']==0].index:
            df_me.loc[i,'p_me'] = main_engine_power(me_power = df_me.loc[i,'mcr'],
                                                    me_type = df_inpt['propulsion_type'].item())
    except:
        pass
    
    return df_me

def load_ae_data(inpt):
    #initialise column dtypes
    int_vals_eng = ['engine_number']
    str_vals_eng = ['engine_type','liquid_fuel_type', 'pilot_fuel_type', 'gas_fuel_type']
    float_vals_eng = ['mcr', 'sfc_liquid_fuel', 'sfc_pilot_fuel', 'sfc_gas_fuel_kj']
    
    #create df_ae df, rename columns and reset index from df_inpt
    df_ae = inpt.iloc[91:100].copy()
    df_ae.columns = df_ae.iloc[0]
    df_ae = df_ae[1:].reset_index(drop=True)
    df_ae.columns.name = None
    #transpose df_ae to set column dtypes
    df_ae = df_ae.T.reset_index()
    df_ae.columns = df_ae.iloc[0]
    df_ae = df_ae[1:11].reset_index(drop=True)
    #set dtypes
    df_ae[int_vals_eng] = df_ae[int_vals_eng].astype(int)
    df_ae[str_vals_eng] = df_ae[str_vals_eng].astype(object)
    df_ae[float_vals_eng] = df_ae[float_vals_eng].astype(float)

    df_ae.dropna(subset='mcr', inplace=True)
    
    return df_ae

def calculate_sfc(df_me, df_ae, cf_dict):
    #calculate sfc of gas fuel in g/kWh for me
    df_me.loc[df_me['engine_type']=='dual_fuel','lcv_gas_fuel'] = [cf_dict[i][0] for i in df_me.loc[df_me['engine_type']=='dual_fuel','gas_fuel_type']]
    df_me.loc[df_me['engine_type']=='dual_fuel','sfc_gas_fuel'] = (df_me.loc[df_me['engine_type']=='dual_fuel','sfc_gas_fuel_kj'] / df_me.loc[df_me['engine_type']=='dual_fuel','lcv_gas_fuel']) * 1000

    #calculate sfc of gas fuel in g/kWh for ae
    try:
        df_ae.loc[df_ae['engine_type']=='dual_fuel','lcv_gas_fuel'] = [cf_dict[i][0] for i in df_ae.loc[df_ae['engine_type']=='dual_fuel','gas_fuel_type']]
        df_ae.loc[df_ae['engine_type']=='dual_fuel','sfc_gas_fuel'] = (df_ae.loc[df_ae['engine_type']=='dual_fuel','sfc_gas_fuel_kj'] / df_ae.loc[df_ae['engine_type']=='dual_fuel','lcv_gas_fuel']) * 1000
    except:
        df_ae[['lcv_gas_fuel', 'sfc_gas_fuel', 'cf_pilot_fuel', 'cf_gas_fuel']] = 0
    
    return df_me, df_ae

def calculate_cf(df_me, df_ae, cf_dict):
    #input cf
    df_me['cf_liquid_fuel'] = [cf_dict[i][1] for i in df_me['liquid_fuel_type']]
    df_me.loc[df_me['engine_type']=='dual_fuel','cf_pilot_fuel'] = [cf_dict[i][1] for i in df_me.loc[df_me['engine_type']=='dual_fuel','pilot_fuel_type']]
    df_me.loc[df_me['engine_type']=='dual_fuel','cf_gas_fuel'] = [cf_dict[i][1] for i in df_me.loc[df_me['engine_type']=='dual_fuel','gas_fuel_type']]

    try:
        df_ae['cf_liquid_fuel'] = [cf_dict[i][1] for i in df_ae['liquid_fuel_type']]
        df_ae.loc[df_ae['engine_type']=='dual_fuel','cf_pilot_fuel'] = [cf_dict[i][1] for i in df_ae.loc[df_ae['engine_type']=='dual_fuel','pilot_fuel_type']]
        df_ae.loc[df_ae['engine_type']=='dual_fuel','cf_gas_fuel'] = [cf_dict[i][1] for i in df_ae.loc[df_ae['engine_type']=='dual_fuel','gas_fuel_type']]
    except:
        pass
    
    return df_me, df_ae

def pto_pae_ratio(df_inpt, df_me, df_ae, p_ae, p_pto):
    #initiate ratio for steam turbine case
    standard_propulsion = ['diesel', 'dual_fuel', 'diesel_electric']
    pto_ratio = (((df_inpt['propulsion_type'].iloc[0] == 'steam_turbine') * 0.85)
                + ((df_inpt['propulsion_type'].iloc[0] in standard_propulsion) * 0.75))

    #calculate pto power and p_ae power for calculation
    if (pto_ratio * p_pto) < p_ae: #p_ae is taken as a ratio of p_ae - p_pto
        # p_pto = p_pto
        p_ae_remain = p_ae - (pto_ratio * p_pto)
        p_pto_remove_me = (pto_ratio * p_pto) / len(df_me)
        p_ae_calc = p_ae_remain / len(df_ae)
        
    elif (pto_ratio * p_pto) >= p_ae: #p_pto is assumed to = p_ae
        p_pto = p_ae / 0.75
        p_ae_remain = 0
        p_pto_remove_me = (pto_ratio * p_pto) / len(df_me)
        p_ae_calc = 0
        
    elif p_pto == 0:
        p_pto_remove_me = 0
        p_ae_calc = p_ae / len(df_ae)
    
    return p_pto_remove_me, p_ae_calc

def update_vref(df_inpt, p_me_deduct):
    if (df_inpt['p_sm_rated'].iloc[0] > 0) or (df_inpt['p_pto_rated'].iloc[0] > 0):
        if df_inpt['v_ref_override'].iloc[0] > 0:
            v_ref = df_inpt['v_ref_override'].iloc[0]
            
        elif df_inpt['speed_power_equ'].iloc[0] == 'p=a*v^b':
            v_ref = ((p_me_deduct / df_inpt['speed_power_a'].iloc[0]) 
                    ** (1 / df_inpt['speed_power_b'].iloc[0]))
            
        elif df_inpt['speed_power_equ'].iloc[0] == 'p=a*v^3+b':
            v_ref = ((p_me_deduct - df_inpt['speed_power_a'].iloc[0]) ** (1 / 3)
                    / df_inpt['speed_power_b'].iloc[0] ** (1 / 3))
            
        elif df_inpt['speed_power_equ'].iloc[0] == 'p=a*v^b+c':
            v_ref = ((p_me_deduct - df_inpt['speed_power_a'].iloc[0]) 
                    ** (1 / df_inpt['speed_power_b'].iloc[0])
                    / df_inpt['speed_power_c'].iloc[0] 
                    ** (1 / df_inpt['speed_power_b'].iloc[0]))
        
    else:
        v_ref = df_inpt['v_ref'].iloc[0]
    
    return v_ref

def fuel_ratio_calc(df_inpt, df_me, df_ae):
    me_mdo = empty_series(df_me['p_me'][(df_me['liquid_fuel_type']=='marine_diesel_oil')&(df_me['engine_type']=='diesel')])
    ae_mdo = empty_series(df_ae['p_ae_calc'][(df_ae['liquid_fuel_type']=='marine_diesel_oil')&(df_ae['engine_type']=='diesel')])

    me_lfo = empty_series(df_me['p_me'][(df_me['liquid_fuel_type']=='light_fuel_oil')&(df_me['engine_type']=='diesel')])
    ae_lfo = empty_series(df_ae['p_ae_calc'][(df_ae['liquid_fuel_type']=='light_fuel_oil')&(df_ae['engine_type']=='diesel')])

    me_hfo = empty_series(df_me['p_me'][(df_me['liquid_fuel_type']=='heavy_fuel_oil')&(df_me['engine_type']=='diesel')])
    ae_hfo = empty_series(df_ae['p_ae_calc'][(df_ae['liquid_fuel_type']=='heavy_fuel_oil')&(df_ae['engine_type']=='diesel')])

    gas_fuel = ['liquefied_petroleum_gas_propane', 'liquefied_petroleum_gas_butane',
                'ethane', 'liquefied_natural_gas', 'methanol', 'ethanol']

    me_gas = empty_series(df_me['p_me'][(df_me['gas_fuel_type'].isin(gas_fuel))&(df_me['engine_type']=='dual_fuel')])
    ae_gas = empty_series(df_ae['p_ae_calc'][(df_ae['gas_fuel_type'].isin(gas_fuel))&(df_ae['engine_type']=='dual_fuel')]) 

    if me_gas + ae_gas == 0:
        fd_gas = 0
    else:
        fd_gas = fuel_ratio(
            v_mdo=df_inpt['v_mdo'].iloc[0], v_lfo=df_inpt['v_lfo'].iloc[0],
            v_hfo=df_inpt['v_hfo'].iloc[0], v_lng=df_inpt['v_lng'].iloc[0],
            power_mdo=me_mdo + ae_mdo,
            power_lfo=me_lfo + ae_lfo,
            power_hfo=me_hfo + ae_hfo,
            power_lng=me_gas + ae_gas)

    df_me['fd_gas'] = np.nan
    df_ae['fd_gas'] = np.nan

    df_me.loc[df_me['engine_type']=='dual_fuel','fd_gas'] = fd_gas
    df_ae.loc[df_ae['engine_type']=='dual_fuel','fd_gas'] = fd_gas

    df_me['fd_gas'].fillna(0, inplace=True)
    df_ae['fd_gas'].fillna(0, inplace=True)

    if fd_gas >= 0.5:
        df_me.loc[
        df_me['engine_type']=='dual_fuel',
        'fd_gas'] = 1
        df_ae.loc[
        df_ae['engine_type']=='dual_fuel',
        'fd_gas'] = 1
    if fd_gas == np.nan:
        fd_gas = 0
    return fd_gas, df_me, df_ae

def me_term_calc(df_me):
    df_me['cf_sfc_liquid'] = np.nan
    df_me['cf_sfc_gas'] = np.nan

    #calculate cf x sfc for diesel powered engines
    df_me['cf_sfc_liquid'] = df_me.loc[:,['cf_liquid_fuel','sfc_liquid_fuel']].product(axis=1)
    #calculate cf x sfc for dual fuel powered engines 
    df_me.loc[
        df_me['engine_type']=='dual_fuel',
        'cf_sfc_gas'] = (df_me.loc[
            df_me['engine_type']=='dual_fuel',
            ['cf_pilot_fuel','sfc_pilot_fuel']].product(axis=1)
    + df_me.loc[
        df_me['engine_type']=='dual_fuel',
        ['cf_gas_fuel','sfc_gas_fuel']].product(axis=1))

    df_me['cf_sfc_gas'].fillna(0, inplace=True)
    #calculate me term (pme x cf_me x sfc_me) including df engines
    df_me['me_term'] = (df_me['p_me_calc']
                        * ((df_me['fd_gas'] * df_me['cf_sfc_gas'])
                        + ((1 - df_me['fd_gas']) * df_me['cf_sfc_liquid'])))

    df_me['pto_term'] = (df_me['pto_remove']
                        * ((df_me['fd_gas'] * df_me['cf_sfc_gas'])
                        + ((1 - df_me['fd_gas']) * df_me['cf_sfc_liquid'])))
    #weighted sum cf_me x sfc_me
    cf_sfc_me = (df_me['me_term'].sum()) / df_me['p_me_calc'].sum()
    #final me term
    me_term = df_me['me_term'].sum()
    pto_term = df_me['pto_term'].sum()
    
    return cf_sfc_me, me_term, pto_term, df_me

def ae_term_calc(df_ae, cf_sfc_me):
    df_ae['cf_sfc_liquid'] = np.nan
    df_ae['cf_sfc_gas'] = np.nan

    #calculate cf x sfc for diesel powered engines
    df_ae['cf_sfc_liquid'] = df_ae.loc[:,['cf_liquid_fuel','sfc_liquid_fuel']].product(axis=1)
    #calculate cf x sfc for dual fuel powered engines 
    df_ae.loc[
        df_ae['engine_type']=='dual_fuel',
        'cf_sfc_gas'] = (df_ae.loc[
            df_ae['engine_type']=='dual_fuel',
            ['cf_pilot_fuel','sfc_pilot_fuel']].product(axis=1)
    + df_ae.loc[
        df_ae['engine_type']=='dual_fuel',
        ['cf_gas_fuel','sfc_gas_fuel']].product(axis=1))

    df_ae['cf_sfc_gas'].fillna(0, inplace=True)
    #calculate ae term (pae x cf_ae x sfc_ae) including df engines
    df_ae['ae_term'] = (df_ae['p_ae_calc']
                        * ((df_ae['fd_gas'] * df_ae['cf_sfc_gas'])
                        + ((1 - df_ae['fd_gas']) * df_ae['cf_sfc_liquid'])))
    #weighted sum cf_ae x sfc_ae
    if df_ae['p_ae_calc'].sum() == 0:
        cf_sfc_ae = cf_sfc_me
    else:
        cf_sfc_ae = (df_ae['ae_term'].sum()) / df_ae['p_ae_calc'].sum()
    #final ae term
    ae_term = df_ae['ae_term'].sum()
    
    return cf_sfc_ae, ae_term, df_ae

def roro_plot_calc(ref_eq_df, dwt, gt):
    if dwt / gt < 0.3:
        ref_eq_df.loc[
            ref_eq_df['ship_type']=='roro_cargo_vehicle', 'a'
            ] = (dwt / gt) ** -0.7 * 780.36
    else:
        ref_eq_df.loc[
            ref_eq_df['ship_type']=='roro_cargo_vehicle', 'a'
            ] = 1812.63
    
    return ref_eq_df

def phase_frac_calc(dwt, dwt_lim):
    if dwt >= dwt_lim['dwt_lim'].iloc[0]:
        phase_1_frac = dwt_lim['phase_1_upper'].iloc[0]
        phase_2_frac = dwt_lim['phase_2_upper'].iloc[0]
        phase_3_frac = dwt_lim['phase_3_upper'].iloc[0]
        
    elif (len(dwt_lim) > 1) and (dwt < dwt_lim['dwt_lim'].iloc[0]) and (dwt > dwt_lim['dwt_lim'].iloc[1]):
        phase_1_frac = np.interp(
            x = dwt,
            xp = [dwt_lim['dwt_lim'].iloc[1], dwt_lim['dwt_lim'].iloc[0]],
            fp = [dwt_lim['phase_1_lower'].iloc[1], dwt_lim['phase_1_upper'].iloc[1]])
        phase_2_frac = np.interp(
            x = dwt,
            xp = [dwt_lim['dwt_lim'].iloc[1], dwt_lim['dwt_lim'].iloc[0]],
            fp = [dwt_lim['phase_2_lower'].iloc[1], dwt_lim['phase_2_upper'].iloc[1]])
        phase_3_frac = np.interp(
            x = dwt,
            xp = [dwt_lim['dwt_lim'].iloc[1], dwt_lim['dwt_lim'].iloc[0]],
            fp = [dwt_lim['phase_3_lower'].iloc[1], dwt_lim['phase_3_upper'].iloc[1]])
    else:
        phase_1_frac = 0
        phase_2_frac = 0
        phase_3_frac = 0
        
    return phase_1_frac, phase_2_frac, phase_3_frac
import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from math import pow, floor
from io import BytesIO


version = 1.0

class common_functions:
    def __init__(self):
        pass

    @staticmethod
    def make_table(name, data):
        # 'function' elementi oluşturuluyor
        func = ET.Element('function', name=name)
        
        # 'table' elementi oluşturuluyor
        table = ET.SubElement(func, 'table')

        # 'independentVar' elementleri oluşturuluyor
        row = ET.SubElement(table, 'independentVar', lookup='row')
        row.text = 'velocities/mach'

        column = ET.SubElement(table, 'independentVar', lookup='column')
        column.text = 'atmosphere/density-altitude'

        # 'tableData' elementi oluşturuluyor
        table_data = ET.SubElement(table, 'tableData')
        table_data.text = data

        return func

    @staticmethod
    def indent(elem, level=0):
        i = "\n" + level*"    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                common_functions.indent(subelem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
        return elem

    @staticmethod
    def save_xml(root, filename):
        # Save the XML file
        tree = ET.ElementTree(root)
        tree.write(filename, xml_declaration=True, encoding='utf-8')

        # Verify the file exists and is well-formed before parsing
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except ET.ParseError as e:
            st.error(f"Error parsing XML file: {e}")
            return

    @staticmethod
    def read_xml(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

class generate:
    def __init__(self):
        pass

    def engine(self, step1_dict):
        engine_name = step1_dict["engine_name"]
        engine_type = step1_dict["engine_type"]
        power_or_thrust = float(step1_dict["power_or_thrust"])
        power_unit = step1_dict["power_unit"]
        afterburning = step1_dict["afterburning"]
        water_injection = step1_dict["water_injection"]
        
        # Yorumlar ekleme
        comments = f"\n  File: {engine_name}.xml\n  Author: Aero-Matic v {version}\n\n  Inputs\n    name: {engine_type}\n    type: {engine_type}\n    power: {power_or_thrust}\n    augmented: {afterburning}\n    injected: {water_injection}\n\n"

        # XML yapısını oluşturma
        root = ET.Element(f"{engine_type}_engine")
        root.append(ET.Comment(comments))
       

        # Motor ismi ekleme
        root.set('name', engine_name)

        # Power unit conversion
        if power_unit == 'kw':
            power_or_thrust *= 1.341
        elif power_unit == 'newtons':
            power_or_thrust *= 0.2248

        # Motor türüne göre XML elementini oluşturma
        if engine_type == 'piston':
            ET.SubElement(root, 'power').text = str(power_or_thrust)
            ET.SubElement(root, "minmp", attrib={"unit":"INHG"}).text = str(10.0)
            ET.SubElement(root, "maxmp", attrib={"unit":"INHG"}).text = str(28.5)
            displ = power_or_thrust * 1.9
            ET.SubElement(root, "displacement", attrib={"unit" : "IN3"}).text = str(displ)
            ET.SubElement(root, 'maxhp').text = str(power_or_thrust)
            ET.SubElement(root, 'cycles').text = str(4)
            ET.SubElement(root, 'idlerpm').text = str(700)
            ET.SubElement(root, 'maxrpm').text = str(2800)
            ET.SubElement(root, 'sparkfaildrop').text = str(0.1)
            ET.SubElement(root, 'volumetric-efficiency').text = str(0.85)
            ET.SubElement(root, 'man-press-lag').text = str(0.1)
            ET.SubElement(root, 'static-friction', attrib={"unit" : "HP"}).text = str(power_or_thrust*0.005)
            ET.SubElement(root, 'starter-torque').text = str(power_or_thrust*0.8)
            ET.SubElement(root, 'starter-rpm').text = "1400"

            stroke = 4.375
            bore = 5.125
            bore_s = pow(bore/2, 2.0) * 3.14159
            n_cylinders = displ / (stroke * bore_s)
            if n_cylinders < 1:
                n_cylinders = 1
            else:
                n_cylinders = floor(n_cylinders+0.5)

            ET.SubElement(root, 'stroke', attrib={"unit" : "IN"}).text = str(4.375)
            ET.SubElement(root, 'bore', attrib={"unit" : "IN"}).text = str(bore)
            ET.SubElement(root, 'cylinders').text = str(n_cylinders)
            ET.SubElement(root, 'compression_ratio').text = "8.0"

            common_functions.indent(root)

            return root

        elif engine_type == 'turbine':
            maxthrust = power_or_thrust*1.5 if afterburning else power_or_thrust
            

            ET.SubElement(root, 'milthrust').text = str(power_or_thrust)
            if (afterburning == "yes"):
                ET.SubElement(root, 'maxthrust').text = str(maxthrust)
                ET.SubElement(root, 'atsfc').text = str(1.7)
                ET.SubElement(root, 'augmented').text = str(1)
                ET.SubElement(root, 'augmethod').text = str(1)
            else:
                ET.SubElement(root, 'augmented').text = str(0)

            ET.SubElement(root, 'bypassratio').text = str(1.0)
            ET.SubElement(root, 'tsfc').text = str(0.8)
            ET.SubElement(root, 'bleed').text = str(0.03)
            ET.SubElement(root, 'idlen1').text = str(30.0)
            ET.SubElement(root, 'idlen2').text = str(60.0)
            ET.SubElement(root, 'maxn1').text = str(100.0)
            ET.SubElement(root, 'maxn2').text = str(100.0)
            ET.SubElement(root, 'injected').text = str(1 if water_injection == "yes" else 0)
            
            idlethrust = ('IdleThrust'
                "    -10000     0     10000   20000   30000   40000   50000   60000\n"
                "0.0  0.0430  0.0488  0.0528  0.0694  0.0899  0.1183  0.1467  0\n"
                "0.2  0.0500  0.0501  0.0335  0.0544  0.0797  0.1049  0.1342  0\n"
                "0.4  0.0040  0.0047  0.0020  0.0272  0.0595  0.0891  0.1203  0\n"
                "0.6  0.0     0.0     0.0     0.0     0.0276  0.0718  0.1073  0\n"
                "0.8  0.0     0.0     0.0     0.0     0.0474  0.0868  0.0900  0\n"
                "1.0  0.0     0.0     0.0     0.0     0.0     0.0552  0.0800  0\n")

            milthrust = ('MilThrust'
            "     -10000       0   10000   20000   30000   40000   50000   60000\n"
            "0.0   1.2600  1.0000  0.7400  0.5340  0.3720  0.2410  0.1490  0\n"
            "0.2   1.1710  0.9340  0.6970  0.5060  0.3550  0.2310  0.1430  0\n"
            "0.4   1.1500  0.9210  0.6920  0.5060  0.3570  0.2330  0.1450  0\n"
            "0.6   1.1810  0.9510  0.7210  0.5320  0.3780  0.2480  0.1540  0\n"
            "0.8   1.2580  1.0200  0.7820  0.5820  0.4170  0.2750  0.1700  0\n"
            "1.0   1.3690  1.1200  0.8710  0.6510  0.4750  0.3150  0.1950  0\n"
            "1.2   1.4850  1.2300  0.9750  0.7440  0.5450  0.3640  0.2250  0\n"
            "1.4   1.5941  1.3400  1.0860  0.8450  0.6280  0.4240  0.2630  0\n")

            # Table elementini oluşturma ve veriyi ekleme
            turbine_idlethust= common_functions.make_table('IdleThrust', idlethrust)
            turbine_milthrust = common_functions.make_table('MilThrust', milthrust)
            root.append(turbine_idlethust)
            root.append(turbine_milthrust)

            if (afterburning == "yes"):
                augthrust = ('AugThrust'
                "      -10000       0   10000   20000   30000   40000   50000   60000\n"
                "0.0    1.1816  1.0000  0.8184  0.6627  0.5280  0.3756  0.2327  0\n"
                "0.2    1.1308  0.9599  0.7890  0.6406  0.5116  0.3645  0.2258  0\n"
                "0.4    1.1150  0.9474  0.7798  0.6340  0.5070  0.3615  0.2240  0\n"
                "0.6    1.1284  0.9589  0.7894  0.6420  0.5134  0.3661  0.2268  0\n"
                "0.8    1.1707  0.9942  0.8177  0.6647  0.5309  0.3784  0.2345  0\n"
                "1.0    1.2411  1.0529  0.8648  0.7017  0.5596  0.3983  0.2467  0\n"
                "1.2    1.3287  1.1254  0.9221  0.7462  0.5936  0.4219  0.2614  0\n"
                "1.4    1.4365  1.2149  0.9933  0.8021  0.6360  0.4509  0.2794  0\n"
                "1.6    1.5711  1.3260  1.0809  0.8700  0.6874  0.4860  0.3011  0\n"
                "1.8    1.7301  1.4579  1.1857  0.9512  0.7495  0.5289  0.3277  0\n"
                "2.0    1.8314  1.5700  1.3086  1.0474  0.8216  0.5786  0.3585  0\n"
                "2.2    1.9700  1.6900  1.4100  1.2400  0.9100  0.6359  0.3940  0\n"
                "2.4    2.0700  1.8000  1.5300  1.3400  1.0000  0.7200  0.4600  0\n"
                "2.6    2.2000  1.9200  1.6400  1.4400  1.1000  0.8000  0.5200  0\n")

                turbine_augthrust = common_functions.make_table('AugThrust', augthrust)
                root.append(turbine_augthrust)

            if (water_injection=="yes"):
                inj = ('Injection'
                "       0       50000\n"
                "0.0    1.2000  1.2000\n"
                "1.0    1.2000  1.2000\n"
                )

                turbine_inj = common_functions.make_table('Injection', inj)
                root.append(turbine_inj)

            

            common_functions.indent(root)

            return root

        elif engine_type == 'turboprop':
            if (power_unit == "horsepower" or power_unit == "pounds"):
                power_or_thrust *= 2.24
        
            ET.SubElement(root, 'milthrust').text = str(power_or_thrust)
            ET.SubElement(root, 'bypassratio').text = str(0.0)
            ET.SubElement(root, 'tsfc').text = str(0.55)
            ET.SubElement(root, 'bleed').text = str(0.03)
            ET.SubElement(root, 'idlen1').text = str(30.0)
            ET.SubElement(root, 'idlen2').text = str(60.0)
            ET.SubElement(root, 'maxn1').text = str(100.0)
            ET.SubElement(root, 'maxn2').text= str(100.0)
            ET.SubElement(root, 'augmented').text = str(0)
            ET.SubElement(root, 'injected').text = str(0)
            #ET.SubElement(root, 'power').text = str(power_or_thrust)

            idlethrust = (
                "IdleThrust\n"
                "-10000       0   10000   20000   30000   40000   50000\n"
                "0.0  0.0430  0.0488  0.0528  0.0694  0.0899  0.1183  0.0\n"
                "0.2  0.0500  0.0501  0.0335  0.0544  0.0797  0.1049  0.0\n"
                "0.4  0.0040  0.0047  0.0020  0.0272  0.0595  0.0891  0.0\n"
                "0.6  0.0     0.0     0.0     0.0276  0.0718  0.0430  0.0\n"
                "0.8  0.0     0.0     0.0     0.0     0.0174  0.0086  0.0\n"
                "1.0  0.0     0.0     0.0     0.0     0.0     0.0     0.0\n"
            )

            milthrust = (
                " MilThrust\n"
                "    -10000       0   10000   20000   30000   40000   50000\n"
                "0.0  1.1260  1.0000  0.7400  0.5340  0.3720  0.2410  0.0\n"
                "0.2  1.1000  0.9340  0.6970  0.5060  0.3550  0.2310  0.0\n"
                "0.4  1.0000  0.6410  0.6120  0.4060  0.3570  0.2330  0.0\n"
                "0.6  0.4430  0.3510  0.2710  0.2020  0.1780  0.1020  0.0\n"
                "0.8  0.0240  0.0200  0.0160  0.0130  0.0110  0.0100  0.0\n"
                "1.0  0.0     0.0     0.0     0.0     0.0     0.0     0.0\n"
            )
            
            # Table elementini oluşturma ve veriyi ekleme
            table_elem = common_functions.make_table('IdleThrust', idlethrust)
            table_elem_2 = common_functions.make_table('MilThrust', milthrust)
            root.append(table_elem)
            root.append(table_elem_2)

            common_functions.indent(root)

        elif engine_type == 'rocket':
            # Roket motor XML elementi oluşturma
            ET.SubElement(root, 'shr').text = str(1.23)
            ET.SubElement(root, 'max_pc').text = str(86556)
            ET.SubElement(root, 'variance').text = str(0.1)
            ET.SubElement(root, 'prop_eff').text = str(0.67)
            ET.SubElement(root, 'maxthrottle').text = str(1.0)
            ET.SubElement(root, 'minthrottle').text = str(0.4)
            ET.SubElement(root, 'slfuelflowmax').text = str(91.5)
            ET.SubElement(root, 'sloxiflowmax').text = str(105.2)

            common_functions.indent(root)
       
        return root 
    
    def aircraft_set(self, step5_dict):
        root = ET.Element('PropertyList')
        
        # sim element
        sim = ET.SubElement(root, 'sim')
        
        # Adding the description and author
        sim.append(ET.Comment("Talking about aircraft on Flightgear GUI"))
        ET.SubElement(sim, 'description').text = step5_dict["description"]
        ET.SubElement(sim, 'author').text = step5_dict["author"]
        ET.SubElement(sim, 'long-description').text = step5_dict["long_description"]
        ET.SubElement(sim, 'aircraft-version').text = step5_dict["aircraft_version"]

        flight_model = step5_dict["flight_model"]

        sim.append(ET.Comment("Engine and fuel information"))
        ET.SubElement(sim, 'fligh-model').text = "jsb" if flight_model == "JSBSim" else "yasim"
        ET.SubElement(sim, 'aero').text = step5_dict["aero_file"]
        ET.SubElement(sim, 'fuel-fraction').text = step5_dict["fuel_Fraction"]

        sim.append(ET.Comment("Engine and fuel information"))
        sound_tag = ET.SubElement(sim, 'sound')
        ET.SubElement(sound_tag, "audible").text = step5_dict["audible"]
        ET.SubElement(sound_tag, "path").text = step5_dict["sound_path"]

        panel_tag = ET.SubElement(sim, 'panel')
        ET.SubElement(panel_tag, "visibility", attrib={"archive":"n"}).text = step5_dict["panelVisibility"]

        model_tag = ET.SubElement(sim, 'model')
        ET.SubElement(model_tag, "path", attrib={"archive":"y"}).text = step5_dict["model_path"]

        previews = ET.SubElement(sim, "previews")
        prev = ET.SubElement(previews, "preview")
        ET.SubElement(prev, 'type').text = 'exterior'
        ET.SubElement(prev, 'path').text = 'Previews/turkey.png'
        ET.SubElement(prev, 'splash').text = 'true'
        
        total_tags = ET.SubElement(sim, "tags")
        
        dizi = step5_dict["tags"].split()
        for i in dizi:
            ET.SubElement(total_tags, "tag").text = i

        rate = ET.SubElement(sim, "rating")
        ET.SubElement(rate, 'FDM').text = str(step5_dict["fdm"])
        ET.SubElement(rate, 'systems').text = str(step5_dict["systems"])
        ET.SubElement(rate, 'cockpit').text = str(step5_dict["cockpit"])
        ET.SubElement(rate, 'model').text = str(step5_dict["model_rating"])

        help = ET.SubElement(sim, "help")
        ET.SubElement(help, 'title').text = step5_dict["help_title"]
        for j in step5_dict["help_lines"].split("\n"):
            ET.SubElement(help, "line").text = j

        rate = ET.SubElement(sim, "view")
        ET.SubElement(rate, 'internal', attrib={"archive": "y"}).text ="true"
        config = ET.SubElement(rate, "config")
        ET.SubElement(config, "x-offset-m", attrib={"archive": "y"}).text = str(step5_dict["x_offset_m"])
        ET.SubElement(config, "y-offset-m", attrib={"archive": "y"}).text = str(step5_dict["y_offset_m"])
        ET.SubElement(config, "z-offset-m", attrib={"archive": "y"}).text = str(step5_dict["z_offset_m"])
        ET.SubElement(config, "pitch-offset-deg").text = str(step5_dict["pitch_offset_deg"])

        consumables = step5_dict["fuel_tanks"]
        consumables = ET.SubElement(sim, "consumables")
        fuel = ET.SubElement(consumables, "fuel")
        
        fuel_row = step5_dict["fuel_tanks"].split("\n")
        fuel_dict = []

        for i in fuel_row:
            fuel_dict.append(i.split("|"))

        lenght_fuel = (len(fuel_dict))

        j = 0
        for i in range (lenght_fuel):
            tank = ET.SubElement(fuel, "tank", attrib={"n": f"{i}"})
            ET.SubElement(tank, "name").text = str(fuel_dict[i][j+1])
            ET.SubElement(tank, "capacity", attrib={"unit": "LBS"}).text = str(fuel_dict[i][j+2])
            ET.SubElement(tank, "selected", attrib={"type": "bool"}).text = "true"
            
        engines = ET.SubElement(root, "engines")
        engine = ET.SubElement(engines, "engine")
        ET.SubElement(engine, "rpm").text = str(step5_dict["rpm"])

        fdm = ET.SubElement(root, "fdm")
        flight = ET.SubElement(fdm, "flight")
        ET.SubElement(flight, "elevator-trim").text = str(step5_dict["aileron-trim"])
        ET.SubElement(flight, "elevator-trim").text = str(step5_dict["elevator-trim"])
        ET.SubElement(flight, "rudder-trim").text = str(step5_dict["rudder-trim"])

        controls = ET.SubElement(root, "controls")
        engin = ET.SubElement(controls, "engines")
        ET.SubElement(engin, "active-engine").text = "0"
        ET.SubElement(engin, "running").text = "true"

        common_functions.indent(root)
        return root
        
    def thruster(self, step4_dict):
        thruster = step4_dict["selected_thruster"] 
        if thruster == "Direct":
            # 'direct' elementi oluşturuluyor ve 'name' attribute'u ekleniyor
            ET.Element('sense').text = "1"
            direct_element = ET.Element('direct', name='direct')

            # İçeriği ekleme (metin veya başka bir element)
            direct_element.append(ET.Comment("There is no tag to add direct file."))

            # Element ağacını oluşturma

            return direct_element

        elif thruster == "Nozzle":
            rocket = ET.Element("nozzle", attrib={"name": f"{step4_dict['nozzle_name']}"})
            ET.SubElement(rocket, "area", attrib = {"unit": f"{step4_dict['area_unit']}"}).text = str(step4_dict["area"])

            common_functions.indent(rocket)
            return rocket
        
        elif thruster == "Rotor":
            ET.Element('sense').text = str()
            rotor = ET.Element("rotor", attrib={"name": f"{step4_dict['name']}"})
            ET.SubElement(rotor, "diameter", attrib={"unit": ""}).text = str(step4_dict["diameter"])
            ET.SubElement(rotor, "numblades").text = str(step4_dict["numblades"])
            ET.SubElement(rotor, "gearratio").text = str(step4_dict["gearratio"])
            ET.SubElement(rotor, "nominalrpm").text = str(step4_dict["nominalrpm"])
            ET.SubElement(rotor, "minrpm").text = str(step4_dict["minrpm"])
            ET.SubElement(rotor, "maxrpm").text = str(step4_dict["maxrpm"])
            ET.SubElement(rotor, "chord", attrib={"unit": ""}).text = str(step4_dict["chord"])
            ET.SubElement(rotor, "liftcurveslope", attrib={"unit": ""}).text = str(step4_dict["liftcurveslope"])
            ET.SubElement(rotor, "twist", attrib={"unit": ""}).text = str(step4_dict["twist"])
            ET.SubElement(rotor, "hingeoffset", attrib={"unit": ""}).text = str(step4_dict["hingeoffset"])
            ET.SubElement(rotor, "flappingmoment", attrib={"unit": ""}).text = str(step4_dict["flappingmoment"])
            ET.SubElement(rotor, "massmoment", attrib={"Xunit": ""}).text = str(step4_dict["massmoment"])
            ET.SubElement(rotor, "polarmoment", attrib={"unit": ""}).text = str(step4_dict["polarmoment"])
            ET.SubElement(rotor, "inflowlag").text = str(step4_dict["inflowlag"])
            ET.SubElement(rotor, "tiplossfactor").text = str(step4_dict["tiplossfactor"])
            ET.SubElement(rotor, "maxbrakepower", attrib={"unit": ""}).text = str(step4_dict["maxbrakepower"])
            ET.SubElement(rotor, "controlmap").text = str(step4_dict["controlmap"])
            ET.SubElement(rotor, "ExternalRPM").text = str(step4_dict["externalrpm"])
            ET.SubElement(rotor, "groundeffectexp").text = str(step4_dict["groundeffectshift"])
            ET.SubElement(rotor, "groundeffectshift", attrib={"unit": ""}).text = str(step4_dict["groundeffectexp"])

            common_functions.indent(rotor)
            return rotor
        
        elif thruster == "Propeller":
            ET.Element('sense').text = str(1)
            propeller = ET.Element('propeller', attrib={"name":f'{step4_dict["propeller_name"]}'})
            ET.SubElement(propeller , "ixx").text = str()
            ET.SubElement(propeller , "diameter", attrib={"unit": "IN"}).text = str(step4_dict["diameter"])
            ET.SubElement(propeller , "numblades").text = str(step4_dict["numblades"])
            ET.SubElement(propeller , "gearratio").text = str(step4_dict["gearratio"])
            ET.SubElement(propeller , "minpitch").text = str()
            ET.SubElement(propeller , "maxpitch").text = str()
            ET.SubElement(propeller , "minrpm").text = str(step4_dict["minrpm"])
            ET.SubElement(propeller , "maxrpm").text = str(step4_dict["maxrpm"])
            ET.SubElement(propeller , "constspeed").text = str(step4_dict["constspeed"])
            ET.SubElement(propeller , "reversepitch").text = str(step4_dict["reversepitch"])
            ET.SubElement(propeller , "ct_factor").text = str(step4_dict["ct_factor"])
            ET.SubElement(propeller , "cp_factor").text = str(step4_dict["cp_factor"])
            ET.SubElement(propeller , "c_tmach").text = str(step4_dict["c_tmach"])
            ET.SubElement(propeller , "c_pmach").text = str(step4_dict["c_pmach"])

            common_functions.indent(propeller)
            return propeller

           



            return thruster

    def model_aircraft(self, step7_dict):
        model = ET.Element("models")

        return model




class Frontend:
    def __init__(self):
        st.set_page_config(layout="wide")
        c, cc = st.columns([0.1, 0.9])
        with c:
            logo = st.image("images/logo.png", width=100)
        with cc:
            st.title("First 7 Steps to Add Your Own Aircraft to Flightgear")

        #st.subheader("What is ",divider=True)
        st.write("FlightGear is a free and open source flight simulation software. Started in 1997, this project provides a platform to which anyone with an interest in flight simulations can contribute. FlightGear can simulate a wide variety of airplanes, airports and flight conditions, so it is used by both flight enthusiasts and professionals for training and entertainment purposes. During the installation phase, you can download the software from the official website and install it on your computer. On the start screen, you can adjust settings such as aircraft selection, airport selection and flight parameters. The flight simulation starts in a realistic cockpit environment and you can manage the aircraft using control systems from real airplanes. FlightGear is extensible, so you can download and add new aircraft models developed by the community. To import aircraft, simply place the downloaded aircraft files into FlightGear's **Aircraft** folder. FlightGear is characterized by realistic flight dynamics, modular structure, extensive scenery options and multiplayer mode. These features allow users to improve their flying skills, experience different airplanes, and create their own simulation content.")
        
        
        im1, im2, im3 = st.columns([0.27, 0.37, 0.36])
        with im1:
            img1 = st.image("images/aircraft.png")
        with im2:
            img2 = st.image("images/cockpit.png")
        with im3:
            img3 = st.image("images/aircraft_2.png")

        st.write("Simulations allow the design and performance of an aircraft to be thoroughly tested in a controlled, virtual environment. This reduces the risk of failure by helping to identify and resolve any issues before the aircraft is ever built or flown. Simulations also allow pilots and engineers to understand how the aircraft will behave under different conditions, such as different weather conditions or flight dynamics. Without these simulations, predicting the real-world performance of an aircraft would be extremely difficult, leading to potentially dangerous and costly mistakes. Simulations are therefore an essential step in the development and certification process of any aircraft, ensuring safety, reliability and efficiency before actual flight operations begin.")
        with st.expander("**Why did we make this application?**"):
            st.write('''
                The reason we made this app is because we realized that for beginners, the process of simulating their own airplanes can sometimes be a slow one. We aim to help you get through the initial stages quickly and efficiently. We've been there ourselves and we know the challenges of this process.!
            ''')

        st.info('**Auxiliary Resources**: The most important sites **[Flightgear is the official site](https://www.flightgear.org/)** to help you where you get stuck. You can also examine the **[JSBSim file](https://jsbsim.sourceforge.net/JSBSimReferenceManual.pdf)**. You can also find the **[Aeromatic site](https://jsbsim.sourceforge.net/aeromatic2.html)** from which we are inspired here!', icon="ℹ️")
        st.warning('Step 1de turboprop ve rocket seçeneklerini, step 5 ve step 7yi deneyebilirsiniz.', icon="⚠️")

        self.step1()
        self.step2()
        self.step4()
        self.step5()
        self.step7()

        footer_col1, footer_col2 = st.columns(2)
        with footer_col1:
            st.write("You've managed to transfer your airplane to FlightGear for the first stage. Now you are on your own! You can add realism to your simulation by adding sound effects and visual customization with various aircraft liveries. The electronics and cockpit enhance the functionality of your aircraft, while thumbnails and previews enhance the visual presentation. GUI information messages and checklists will improve the user experience, while a separate menu will make your simulation more accessible. You can use FlightGear's original site for these steps. Good luck!")
            st.write("**Version 1.0**")
            st.write("*Contact me if you want to point out shortcomings or get involved in development.*", "**Tuğçe Ulucan**")
            st.image("images/turkish_flag.jpg", width=350)
        with footer_col2:
            data = pd.DataFrame({'latitude': [41.015137],'longitude': [28.979530]})
            st.map(data, zoom=10, color='#0044ff')
    
    def step1(self):
        st.subheader("Step 1: The Engine Configuration", divider=True)
        st.write("This step is to define the engine configuration...")

        step1_dict = {}  # Create an empty dictionary

        with st.expander("**STEP :one:**"):
            with st.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    with st.container(border=True):
                        step1_dict["engine_name"] = st.text_input("Engine Name", value="my_engine")
                        step1_dict["engine_type"] = st.radio("Engine Type", ['piston', 'turbine', 'turboprop', 'rocket'])

                with col2:
                    with st.container(border=True):
                        step1_dict["power_or_thrust"] = st.text_input("Engine Power or Thrust (per engine, without afterburning)", value="1000.0")
                        step1_dict["power_unit"] = st.radio("Unit", ['horsepower', 'kw', 'pounds', 'newtons'], index=0)

                with col3:
                    with st.container(border=True):
                        step1_dict["afterburning"] = st.radio("Augmentation (afterburning) Installed?", ['yes', 'no'], index=1)
                        step1_dict["water_injection"] = st.radio("Water Injection Installed?", ['yes', 'no'], index=1)

                if st.button(label='Generate Engine File'):
                    # XML dosyasını oluşturma ve kaydetme
                    engine_xml = gener.engine(step1_dict)
                    common_functions.save_xml(engine_xml, f"{step1_dict['engine_name']}.xml")

                    xml_data = common_functions.read_xml(f"{step1_dict['engine_name']}.xml")
                    st.code(xml_data, language="python", line_numbers=False)

                    st.download_button(
                        label="Download my_engine.xml",
                        data=xml_data,
                        file_name="my_engine.xml",
                        mime="application/xml")

    def step2(self):
        st.subheader("Step 2: The Prop configuration (if applicable)...", divider=True)
        st.write("This step is to define the propeller configuration. The type of propeller used on the aircraft and its maximum RPM are configured in this step. This step is required when using a propeller-based engine configuration.")
        with st.expander("**STEP :two:**"):
            with st.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    with st.container(border=True):        
                        engine_power = st.text_input("Engine Power (per engine))", value="1000.0")
                        eng_power_unit = st.radio("", ['horsepower', 'kw'], index=0)
                with col2:
                    with st.container(border=True):
                        maximum_eng_rpm = st.text_input("Maximum Engine RPM", value="2700")
                        pitch = st.radio("Pitch", ['fixed', 'variable'], index=0)
                with col3:
                    with st.container(border=True):
                        propeller_diameter = st.text_input("Propeller Diameter", value="8")
                        propeller_unit = st.radio("", ['feet', 'inches', 'meters'], index=0)

                # Formu oluştur
                if st.button("Generate 2"):
                    st.write("Engine Name:", engine_power)
                    st.write("Engine Type:", eng_power_unit)
                    st.write(f"Engine Power or Thrust: {maximum_eng_rpm} {pitch}")
                    st.write("Augmentation (afterburning) Installed?:", propeller_unit)
                    st.write("Water Injection Installed?:", propeller_diameter)
                    st.write("You are now ready to have Aeromatic generate your file. Aeromatic will create a file called `engine.php`, which is your engine configuration file. You will need to save this file with a filename of the form `engine_name.xml`.")         
    
    def step4(self):
        st.subheader("Step 4: The Thruster Configuration", divider=True)
        st.write("This step is to define the thruster configuration of the aircraft. If the aircraft has additional thruster systems, they are configured in this step. In this step, parameters such as thruster layout and power outputs are determined.") 
        step4_dict = {}
        with st.expander("**STEP :four:**"):
            with st.container():
                # Motor türleri
                motor_types = ["Electric", "Piston", "Rocket", "Turbine", "TurboProp"]

                # Thruster tiplerini motor türlerine göre eşleştirme
                thruster_options = {
                    "Electric": ["Direct", "Propeller", "Rotor"],
                    "Piston": ["Propeller", 'Rotor'],
                    "Rocket": ["Nozzle"],
                    "Turbine": ["Direct"],
                    "TurboProp": ["Propeller", 'Rotor']
                }

                # Motor türü seçimi
                step4_dict["selected_motor"] = st.selectbox("Select Engine Type", motor_types)

                # Seçilen motor türüne göre thruster tiplerini göster
                if step4_dict["selected_motor"]:
                    selected_thruster = st.selectbox("Select Thruster Type", thruster_options[step4_dict["selected_motor"]])
                    step4_dict["selected_thruster"] = selected_thruster
                    if selected_thruster == "Direct":
                        st.text("No configuration required for direct thruster.")
                        # XML dosyasını oluşturma ve kaydetme
                    

                    elif selected_thruster == "Nozzle":
                        step4_dict["nozzle_name"] = st.text_input("Nozzle Name")
                        step4_dict["area_unit"] = st.selectbox("Area Unit", ["FT2", "M2", "IN2"])
                        step4_dict["area"] = st.number_input("Nozzle Area", min_value=0.0)
                        #nozzle(nozzle_name, area_unit, area)

                    elif selected_thruster == "Propeller":
                        prop_col1, prop_col2, prop_col3 = st.columns(3)
                        
                        step4_dict["propeller_name"] = st.text_input("Propeller Name", "")
                        with prop_col1:
                            step4_dict["ixx"] = st.number_input("Rotational İnertia", min_value=0.0)
                            step4_dict["diameter"] = st.number_input("Propeller disk diameter (IN)", min_value=0.0)
                            step4_dict["numblades"] = st.number_input("Number of Blades", min_value=1, value=1)
                            step4_dict["gearratio"] = st.number_input("Ratio of (engine rpm)/(prop rpm)", value=0.0)
                        with prop_col2:    
                            step4_dict["minpitch"] = st.number_input("Minimum Pitch", min_value=0.0)
                            step4_dict["maxpitch"] = st.number_input("Maximum Pitch", min_value=0.0)
                            step4_dict["minrpm"] = st.number_input("Minimum rpm target for constant speed propeller", value=1.0)
                            step4_dict["maxrpm"] = st.number_input("Maximum rpm target for constant speed propeller", value=0.0)
                        with prop_col3:
                            step4_dict["reversepitch"] = st.number_input("Reverse Pitch", min_value=0.0)
                            step4_dict["ixx_unit"] = st.selectbox("İnertia Unit", ["SLUG*FT2", "KG*M2"])
                            step4_dict["constspeed"] = st.number_input("1 = constant speed mode, 0 = manual pitch mode", min_value=0, max_value=1)
                            step4_dict["reversepitch"] = st.number_input("Blade pitch angle for reverse", min_value=0.0)
                        
                        prop1_col1, prop2_col2 = st.columns(2)
                        with prop1_col1:
                            step4_dict["ct_factor"] = st.text_area("A multiplier for the coefficients of thrust", value="0.0   0.0580\n0.1   0.0620\n0.2   0.0600\n0.3   0.0580\n0.4   0.0520\n0.5   0.0457\n0.6   0.0436\n0.8   0.0372\n0.9   0.0299\n1.0   0.0202\n1.2   0.0075\n1.3   0.0111\n1.4   0.0202\n1.5   0.0280\n1.6   0.0346\n1.7   0.0389\n1.8   0.0421\n1.9   0.0436")
                            step4_dict["c_tmach"] = st.text_area("C_PMACH Tablosu", value="0.0   0.0580\n0.1   0.0620\n0.2   0.0600\n0.3   0.0580\n0.4   0.0520\n0.5   0.0457\n0.6   0.0436\n0.8   0.0372\n0.9   0.0299\n1.0   0.0202\n1.2   0.0075\n1.3   0.0111\n1.4   0.0202\n1.5   0.0280\n1.6   0.0346\n1.7   0.0389\n1.8   0.0421\n1.9   0.0436")
                        with prop2_col2:
                            step4_dict["cp_factor"] = st.text_area("A multiplier for the coefficients of power", value="0.0   0.0580\n0.1   0.0620\n0.2   0.0600\n0.3   0.0580\n0.4   0.0520\n0.5   0.0457\n0.6   0.0436\n0.8   0.0372\n0.9   0.0299\n1.0   0.0202\n1.2   0.0075\n1.3   0.0111\n1.4   0.0202\n1.5   0.0280\n1.6   0.0346\n1.7   0.0389\n1.8   0.0421\n1.9   0.0436")
                            step4_dict["c_pmach"] = st.text_area("C_TMACH Tablosu", value="                     -10         0                15                 25            35            45            55        \n-0.2      -0.0734    0.0413    0.1503    0.1842    0.2030    0.2142    0.1974    \n0.0      -0.1090    0.0000    0.1503    0.1842    0.2030    0.2162    0.2021    \n0.2      -0.1222   -0.0376    0.1297    0.1804    0.2001    0.2162    0.2021    \n0.4      -0.1222   -0.0873    0.0977    0.1786    0.1963    0.2142    0.2021    \n0.6      -0.1222   -0.1222    0.0517    0.1607    0.1879    0.2087    0.1992    \n0.8      -0.1222   -0.1222    0.0029    0.1203    0.1824    0.2012    0.1992    \n1.0      -0.1222   -0.1222   -0.0489    0.0734    0.1748    0.1908    0.1974    \n1.2      -0.1222   -0.1222   -0.1006    0.0226    0.1437    0.1842    0.1974    \n1.4      -0.1222   -0.1222   -0.1222   -0.0329    0.1034    0.1813    0.1936    \n1.8      -0.1222   -0.1222   -0.1222   -0.1222    0.0095    0.1503    0.1842    \n2.0      -0.1222   -0.1222   -0.1222   -0.1222   -0.0376    0.1174    0.1834    \n3.0      -0.1222   -0.1222   -0.1222   -0.1222   -0.1222   -0.0734    0.0320    \n4.0      -0.1222   -0.1222   -0.1222   -0.1222   -0.1222   -0.1222   -0.1137   \n6.0      -0.1222   -0.1222   -0.1222   -0.1222   -0.1222   -0.1222   -0.1222   ")
                        
                            
                    elif selected_thruster == "Rotor":
                        rotor_col1, rotor_col2, rotor_col3 = st.columns(3)
                        with rotor_col1:
                            step4_dict["name"] = st.text_input("Rotor Name", "")
                            step4_dict["diameter"] = st.number_input("Diameter (LENGTH)", value=0.0)
                            step4_dict["numblades"] = st.number_input("Number of Blades", min_value=1, value=1)
                            step4_dict["gearratio"] = st.number_input("Gear Ratio", value=0.0)
                            step4_dict["nominalrpm"] = st.number_input("Nominal RPM", value=0.0)
                            step4_dict["minrpm"] = st.number_input("Minimum RPM", value=1.0)
                            step4_dict["maxrpm"] = st.number_input("Maximum RPM", value=0.0)
                        with rotor_col2:
                            step4_dict["chord"] = st.number_input("Chord (LENGTH)", value=0.0)
                            step4_dict["liftcurveslope"] = st.number_input("Lift Curve Slope (1/RAD)", value=0.0)
                            step4_dict["twist"] = st.number_input("Twist (ANGLE)", value=0.0)
                            step4_dict["hingeoffset"] = st.number_input("Hinge Offset (LENGTH)", value=0.0)
                            step4_dict["flappingmoment"] = st.number_input("Flapping Moment (MOMENT)", value=0.0)
                            step4_dict["massmoment"] = st.number_input("Mass Moment (SLUG*FT)", value=0.0)
                            step4_dict["polarmoment"] = st.number_input("Polar Moment (MOMENT)", value=0.0)
                        with rotor_col3:    
                            step4_dict["inflowlag"] = st.number_input("Inflow Lag (sec)", value=0.0)
                            step4_dict["tiplossfactor"] = st.number_input("Tip Loss Factor", value=1.0)
                            step4_dict["maxbrakepower"] = st.number_input("Max Brake Power (POWER)", value=0.0)
                            step4_dict["controlmap"] = st.selectbox("Control Map", options=['MAIN', 'TAIL', 'TANDEM'])
                            step4_dict["externalrpm"] = st.number_input("External RPM", value=0.0)
                            step4_dict["groundeffectshift"] = st.number_input("Ground Effect Shift (LENGTH)", value=0.0)
                            step4_dict["groundeffectexp"] = st.number_input("Ground Effect Exponent", value=0.0)
        
                    # Seçilen motor ve thruster türüne göre alınan verileri gösterebilirsiniz.
                    if st.button(label='Generate thruster.xml'): 
                        # XML dosyasını oluşturma ve kaydetme
                        thruster_xml = gener.thruster(step4_dict)

                        # XML verisini dosya olarak kaydetme (geçici)
                        tree = ET.ElementTree(thruster_xml)
                        tree.write("thruster.xml", xml_declaration=True, encoding='utf-8')

                        # Kaydedilen XML dosyasını okumak ve hatasız olup olmadığını kontrol etmek
                        tree = ET.parse("thruster.xml")
                        root = tree.getroot()

                        # XML verisini string olarak almak
                        xml_data = ET.tostring(thruster_xml, encoding='utf-8', method='xml')

                        # XML verisini indirilebilir hale getirmek için BytesIO ile akışa çevirme
                        xml_bytes = BytesIO(xml_data)

                        # XML verisini indirilebilir hale getir
                        st.download_button(
                            label="Download XML File",
                            data=xml_bytes,
                            file_name="thruster.xml",
                            mime="application/xml"
                        )

    def step5(self):
        st.subheader("Step 5: Root directory aircraft-set Configuration", divider=True)
        #view, consumables, engines controls fdm eksik.
        st.write("This step defines the aircraft-set configuration file located in the root directory of the aircraft. This file contains the general description of the aircraft, its version, sound and panel settings. Also, details such as the fuel tanks used for the aircraft, model path and preview images are defined in this step.")
        
        step5_dict = {}  # Create an empty dictionary

        with st.expander("**STEP :five:** | Root directory aircraft-set Configuration "):
            with st.container():
                with st.container(border=True):
                        cl1, cl2, cl3 = st.columns(3)
                        with cl1:
                            step5_dict["description"] = st.text_input('Description', 'Mandalina 1.0| IDEALAB (2024)')
                        with cl2:
                            step5_dict["author"] = st.text_input('Author', 'Edip Sevincer(Manager), Selami Korkmaz(Designer)...')
                        with cl3:
                            step5_dict["aircraft_version"] = st.text_input('Aircraft Version', '1.0')

                with st.container(border=True):
                    step5_dict["long_description"] = st.text_area('Long Description', 'Mandalina is an unmanned aerial vehicle produced by the IDEALAB company...')
                    cl4, cl5, cl6 = st.columns(3)
                    with cl4:
                        step5_dict["aero_file"] = st.text_input("Aerodynamic Model File Name", value="aircraft")
                    with cl5:
                        step5_dict["fuel_Fraction"] = st.text_input("Fuel Fraction", value="1.0")
                    with cl6:
                        step5_dict["sound_path"] = st.text_input('Sound Path', 'Aircraft/Deneme/Sounds/mandalina-sound.xml')
                    
                with st.container(border=True):
                    cl7, cl8, cl9 = st.columns(3)
                    with cl7:
                        step5_dict["flight_model"] = st.radio("Flight Model", ['JSBSim', 'YASim'], index=1)
                    with cl8:
                        step5_dict["panelVisibility"] = st.radio("Aircraft Panel Visibility", ['True', 'False'], index=1)
                    with cl9:
                        step5_dict["audible"] = st.radio("Sound Audible", ['True', 'False'], index=1)

                with st.container(border=True):
                    step5_dict["model_path"] = st.text_input('Model Path', 'Aircraft/Deneme/Models/Deneme.xml')
                    #step5_dict["previews"] = st.text_area('Preview Paths', 'Previews/prev.jpg\nPreviews/prev1.jpg\n...')
                    step5_dict["tags"] = st.text_area('Tags', 'high-wing\nretractable-gear\nsingle-engine\n')
                    step5_dict["help_title"] = st.text_input('Help Title', 'Mandalina, Version 1.0 (IL-170)')
                    step5_dict["help_lines"] = st.text_area('Help Lines', 'Cruise speed: 0.2 Mach\nNever-exceed (Vne): 0.6 Mach\n')
                    step5_dict["fuel_tanks"] = st.text_area('Fuel Tanks (Format: n|name|capacity)', '0|6L-Left Tank|13.2\n1|6L-Right Tank|13.2\n')

                with st.container(border=True):
                    cl10, cl11, cl12, cl13 = st.columns(4)
                    with cl10:
                        step5_dict["fdm"] = st.text_input('FDM Rating', '2')
                    with cl11:
                        step5_dict["systems"] = st.text_input('Systems Rating', '1')
                    with cl12:
                        step5_dict["cockpit"] = st.text_input('Cockpit Rating', '0')
                    with cl13:
                        step5_dict["model_rating"] = st.text_input('Model Rating', '2')

                    cl14, cl15, cl16, cl17 = st.columns(4)
                    with cl14:
                        step5_dict["x_offset_m"] = st.text_input('X-Offset (m)', '0.0')
                    with cl15:
                        step5_dict["y_offset_m"] = st.text_input('Y-Offset (m)', '-0.3')
                    with cl16:
                        step5_dict["z_offset_m"] = st.text_input('Z-Offset (m)', '0.9')
                    with cl17:
                        step5_dict["pitch_offset_deg"] = st.text_input('Pitch Offset (deg)', '-8')

                    cl18, cl19, cl20, cl21 = st.columns(4)
                    with cl18:
                        step5_dict["rpm"] = st.number_input("Rpm", min_value =500 , step=200)
                    with cl19:
                        step5_dict["aileron-trim"] = st.number_input("Aileron-trim",  value=0.00)
                    with cl20:
                        step5_dict["elevator-trim"] = st.number_input("Elevator-trim",  value=0.00)
                    with cl21:
                        step5_dict["rudder-trim"] = st.number_input("Rudder-Trim",  value= 0.00)

                
                if st.button(label='Generate aircraft-set.xml'):
                    # XML dosyasını oluşturma ve kaydetme
                    set_xml = gener.aircraft_set(step5_dict)

                    # XML verisini dosya olarak kaydetme (geçici)
                    tree = ET.ElementTree(set_xml)
                    tree.write("aircraft-set.xml", xml_declaration=True, encoding='utf-8')

                    # Kaydedilen XML dosyasını okumak ve hatasız olup olmadığını kontrol etmek
                    try:
                        tree = ET.parse("aircraft-set.xml")
                        root = tree.getroot()
                    except ET.ParseError as e:
                        st.error(f"Error parsing XML file: {e}")
                        return

                    # XML verisini string olarak almak
                    xml_data = ET.tostring(set_xml, encoding='utf-8', method='xml')

                    # XML verisini indirilebilir hale getirmek için BytesIO ile akışa çevirme
                    xml_bytes = BytesIO(xml_data)

                    # XML verisini indirilebilir hale getir
                    st.download_button(
                        label="XML Dosyasını İndir",
                        data=xml_bytes,
                        file_name="mandalina.xml",
                        mime="application/xml"
                    )

    def step7(self):
        st.subheader("Step 7: Models Directory Aircraft File Configuration", divider=True)
        st.write("This step defines the configuration files located in the models directory of the aircraft. These files contain the physical model of the aircraft, its moving parts (ailerons, flaps, rudders, etc.) and other visual components. This step is used to configure the visual and physical representation of the aircraft.")
        with st.expander("**STEP :seven:** | Models Directory Aircraft File Configuration"):
            with st.container():
                # Available aircraft parts
                parts = ["Ailerons", "Elevator", "Rudder", "Flaps", "Landing Gear", "Canards", "Slats"]
                path_name = st.text_input("**.AC File Path Name**", "aircraft.ac")
                select_parts = st.multiselect("Which surfaces will you give movement/animation to?", parts)
                total_data = {}
                if st.button("Generate parts"):
                    if "Ailerons" in select_parts:
                                st.write("**Ailerons**")
                                c1, c2, c3, c4, c5 = st.columns(5)
                                with c1:
                                    total_data['Aileron_type'] = st.selectbox("Type", ['rotate'])
                                with c2: 
                                    total_data['Aileron_object-name'] = st.text_input("Object file name", "left_canard.079")
                                with c3: 
                                    total_data['Aileron_property'] = st.text_input("Property", "controls/flight/aileron")
                                with c4:
                                    total_data['Aileron_factor'] = st.text_input("Factor", "20")
                                with c5:
                                    total_data['Aileron_offset-deg'] = st.text_input("Offset-Deg", "0")

                                c1, c2, c3, c4, c5, c6 = st.columns(6)
                                with c1:
                                    total_data['Aileron_x1'] = st.number_input("Aileron _a value", value=0.0, step=0.01)
                                with c2:
                                    total_data['Aileron_y1'] = st.number_input("Aileron-a value", value=0.0, step=0.01)
                                with c3:
                                    total_data['Aileron_z'] = st.number_input("Aileron z1-a value", value=0.0, step=0.01)
                                with c4:
                                    total_data['Aileron_x2'] = st.number_input("Aileron x1_a value", value=0.0, step=0.01)
                                with c5:
                                    total_data['Aileron_y2'] = st.number_input("Aileron y1-a value", value=0.0, step=0.01)
                                with c6:
                                    total_data['Aileron_z2'] = st.number_input("Aileron z1-sa value", value=0.0, step=0.01)
                
                    if "Elevator" in select_parts:
                                st.write("**Elevator**")
                                c1, c2, c3, c4, c5 = st.columns(5)
                                with c1:
                                    total_data['Elevator_type'] = st.selectbox("Elevator Type", ['rotate'])
                                with c2: 
                                    total_data['Elevator_object-name'] = st.text_input("Elevator Object file name", "left_canard.079")
                                with c3: 
                                    total_data['Elevator_property'] = st.text_input("Elevator Property", "controls/flight/aileron")
                                with c4:
                                    total_data['Elevator_factor'] = st.text_input("Elevator Factor", "20")
                                with c5:
                                    total_data['Elevator_offset-deg'] = st.text_input("Elevator Offset-Deg", "0")


                                c1, c2, c3, c4, c5, c6 = st.columns(6)
                                with c1:
                                    total_data['Elevator_x1'] = st.number_input("Elevator x1 value", value=0.0, step=0.01)
                                with c2:
                                    total_data['Elevator_y1'] = st.number_input("Elevator y1 value", value=0.0, step=0.01)
                                with c3:
                                    total_data['Elevator_z1'] = st.number_input("Elevator z1 value", value=0.0, step=0.01)
                                with c4:
                                    total_data['Elevator_x2'] = st.number_input("Elevator x2 value", value=0.0, step=0.01)
                                with c5:
                                    total_data['Elevator_y2'] = st.number_input("Elevator y2 value", value=0.0, step=0.01)
                                with c6:
                                    total_data['Elevator_z2'] = st.number_input("Elevator z2 value", value=0.0, step=0.01)

                    if "Rudder" in select_parts:
                                st.write("**Rudder**")
                                c1, c2, c3, c4, c5 = st.columns(5)
                                with c1:
                                    total_data['Rudder_type'] = st.selectbox("Rudder Type", ['rotate'])
                                with c2: 
                                    total_data['Rudder_object-name'] = st.text_input("Rudder Object file name", "left_canard.079")
                                with c3: 
                                    total_data['Rudder_property'] = st.text_input("Rudder Property", "controls/flight/aileron")
                                with c4:
                                    total_data['Rudder_factor'] = st.text_input("Rudder Factor", "20")
                                with c5:
                                    total_data['Rudder_offset-deg'] = st.text_input("Rudder Offset-Deg", "0")


                                c1, c2, c3, c4, c5, c6 = st.columns(6)
                                with c1:
                                    total_data['Rudder_x1'] = st.number_input("Rudder x1 value", value=0.0, step=0.01)
                                with c2:
                                    total_data['Rudder_y1'] = st.number_input("Rudder y1 value", value=0.0, step=0.01)
                                with c3:
                                    total_data['Rudder_z1'] = st.number_input("Rudder z1 value", value=0.0, step=0.01)
                                with c4:
                                    total_data['Rudder_x2'] = st.number_input("Rudder x2 value", value=0.0, step=0.01)
                                with c5:
                                    total_data['Rudder_y2'] = st.number_input("Rudder y2 value", value=0.0, step=0.01)
                                with c6:
                                    total_data['Rudder_z2'] = st.number_input("Rudder z2 value", value=0.0, step=0.01)

                    if "Landing Gear" in select_parts:
                                st.write("**Landing Gear**")
                                c1, c2, c3, c4, c5 = st.columns(5)
                                with c1:
                                    total_data['Landing_Gear_type'] = st.selectbox("Landing Gear Type", ['rotate'])
                                with c2: 
                                    total_data['Landing_Gear_object-name'] = st.text_input("Landing Gear Object file name", "left_landing_gear.079")
                                with c3: 
                                    total_data['Landing_Gear_property'] = st.text_input("Landing Gear Property", "controls/flight/aileron")
                                with c4:
                                    total_data['Landing_Gear_factor'] = st.text_input("Landing Gear Factor", "20")
                                with c5:
                                    total_data['Landing_Gear_offset-deg'] = st.text_input("Landing Gear Offset-Deg", "0")

                                c1, c2, c3, c4, c5, c6 = st.columns(6)
                                with c1:
                                    total_data['Landing_Gear_x1'] = st.number_input("Landing Gear x1 value", value=0.0, step=0.01)
                                with c2:
                                    total_data['Landing_Gear_y1'] = st.number_input("Landing Gear y1 value", value=0.0, step=0.01)
                                with c3:
                                    total_data['Landing_Gear_z1'] = st.number_input("Landing Gear z1 value", value=0.0, step=0.01)
                                with c4:
                                    total_data['Landing_Gear_x2'] = st.number_input("Landing Gear x2 value", value=0.0, step=0.01)
                                with c5:
                                    total_data['Landing_Gear_y2'] = st.number_input("Landing Gear y2 value", value=0.0, step=0.01)
                                with c6:
                                    total_data['Landing_Gear_z2'] = st.number_input("Landing Gear z2 value", value=0.0, step=0.01)


                                c1, c2, c3, c4, c5, c6 = st.columns(6)
                                with c1:
                                    total_data['Landing_Gear_x1'] = st.number_input("Landing_Gear x1 value", value=0.0, step=0.01)
                                with c2:
                                    total_data['Landing_Gear_y1'] = st.number_input("Landing_Gear y1 value", value=0.0, step=0.01)
                                with c3:
                                    total_data['Landing_Gear_z1'] = st.number_input("Landing_Gear z1 value", value=0.0, step=0.01)
                                with c4:
                                    total_data['Rudder_x2'] = st.number_input("Landing_Gear x2 value", value=0.0, step=0.01)
                                with c5:
                                    total_data['Landing_Gear_y2'] = st.number_input("Landing_Gear y2 value", value=0.0, step=0.01)
                                with c6:
                                    total_data['Landing_Gear_z2'] = st.number_input("Landing_Gear z2 value", value=0.0, step=0.01)

                    if "Canards" in select_parts:
                                st.write("**Canards**")
                                c1, c2, c3, c4, c5 = st.columns(5)
                                with c1:
                                    total_data['Canards_type'] = st.selectbox("Canards Type", ['rotate'])
                                with c2: 
                                    total_data['Canards_object-name'] = st.text_input("Canards Object file name", "left_canard.079")
                                with c3: 
                                    total_data['Canards_property'] = st.text_input("Canards Property", "controls/flight/aileron")
                                with c4:
                                    total_data['Canards_factor'] = st.text_input("Canards Factor", "20")
                                with c5:
                                    total_data['Canards_offset-deg'] = st.text_input("Canards Offset-Deg", "0")

                                c1, c2, c3, c4, c5, c6 = st.columns(6)
                                with c1:
                                    total_data['Canards_x1'] = st.number_input("Canards x1 value", value=0.0, step=0.01)
                                with c2:
                                    total_data['Canards_y1'] = st.number_input("Canards y1 value", value=0.0, step=0.01)
                                with c3:
                                    total_data['Canards_z1'] = st.number_input("Canards z1 value", value=0.0, step=0.01)
                                with c4:
                                    total_data['Canards_x2'] = st.number_input("Canards x2 value", value=0.0, step=0.01)
                                with c5:
                                    total_data['Canards_y2'] = st.number_input("Canards y2 value", value=0.0, step=0.01)
                                with c6:
                                    total_data['Canards_z2'] = st.number_input("Canards z2 value", value=0.0, step=0.01)

                    if "Flaps" in select_parts:
                                st.write("**Flaps**")
                                c1, c2, c3, c4, c5 = st.columns(5)
                                with c1:
                                    total_data['Flaps_type'] = st.selectbox("Flaps Type", ['rotate'])
                                with c2: 
                                    total_data['Flaps_object-name'] = st.text_input("Flaps Object file name", "left_canard.079")
                                with c3: 
                                    total_data['Flaps_property'] = st.text_input("Flaps Property", "controls/flight/aileron")
                                with c4:
                                    total_data['Flaps_factor'] = st.text_input("Flaps Factor", "20")
                                with c5:
                                    total_data['Flaps_offset-deg'] = st.text_input("Flaps Offset-Deg", "0")


                                c1, c2, c3, c4, c5, c6 = st.columns(6)
                                with c1:
                                    total_data['Flaps_x1'] = st.number_input("Flaps x1 value", value=0.0, step=0.01)
                                with c2:
                                    total_data['Flaps_y1'] = st.number_input("Flaps y1 value", value=0.0, step=0.01)
                                with c3:
                                    total_data['Flaps_z1'] = st.number_input("Flaps z1 value", value=0.0, step=0.01)
                                with c4:
                                    total_data['Flaps_x2'] = st.number_input("Flaps x2 value", value=0.0, step=0.01)
                                with c5:
                                    total_data['Flaps_y2'] = st.number_input("Flaps y2 value", value=0.0, step=0.01)
                                with c6:
                                    total_data['Flaps_z2'] = st.number_input("Flaps z2 value", value=0.0, step=0.01)

                    if st.button("XML BUTTON"):
                        # XML dosyasını oluşturma ve kaydetme
                        model_xml = gener.model_aircraft(total_data)

                        # XML verisini dosya olarak kaydetme (geçici)
                        tree = ET.ElementTree(model_xml)
                        tree.write("models.xml", xml_declaration=True, encoding='utf-8')

                        # Kaydedilen XML dosyasını okumak ve hatasız olup olmadığını kontrol etmek
                        try:
                            tree = ET.parse("aircraft-set.xml")
                            root = tree.getroot()
                        except ET.ParseError as e:
                            st.error(f"Error parsing XML file: {e}")
                            return

                        # XML verisini string olarak almak
                        xml_data = ET.tostring(model_xml, encoding='utf-8', method='xml')

                        # XML verisini indirilebilir hale getirmek için BytesIO ile akışa çevirme
                        xml_bytes = BytesIO(xml_data)

                        # XML verisini indirilebilir hale getir
                        st.download_button(
                            label="Models XML Dosyasını İndir",
                            data=xml_bytes,
                            file_name="zircraft.xml",
                            mime="application/xml"
                        )



if __name__ == "__main__":
    # Eğer bu dosya direkt çalıştırılırsa aşağıdaki kod çalışır.
    gener = generate()
    front = Frontend()

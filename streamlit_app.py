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
        self.step5()

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



if __name__ == "__main__":
    # Eğer bu dosya direkt çalıştırılırsa aşağıdaki kod çalışır.
    gener = generate()
    front = Frontend()

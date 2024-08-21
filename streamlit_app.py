import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from math import pow, floor

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
        
        # Power unit conversion
        if power_unit == 'kw':
            power_or_thrust *= 1.341
        elif power_unit == 'newtons':
            power_or_thrust *= 0.2248

        # Motor türüne göre XML elementini oluşturma
        if engine_type == 'piston':
            engine = ET.Element('piston_engine')
            ET.SubElement(engine, 'power').text = str(power_or_thrust)
            ET.SubElement(engine, "minmp", attrib={"unit":"INHG"}).text = str(10.0)
            ET.SubElement(engine, "maxmp", attrib={"unit":"INHG"}).text = str(28.5)
            displ = power_or_thrust * 1.9
            ET.SubElement(engine, "displacement", attrib={"unit" : "IN3"}).text = str(displ)
            ET.SubElement(engine, 'maxhp').text = str(power_or_thrust)
            ET.SubElement(engine, 'cycles').text = str(4)
            ET.SubElement(engine, 'idlerpm').text = str(700)
            ET.SubElement(engine, 'maxrpm').text = str(2800)
            ET.SubElement(engine, 'sparkfaildrop').text = str(0.1)
            ET.SubElement(engine, 'volumetric-efficiency').text = str(0.85)
            ET.SubElement(engine, 'man-press-lag').text = str(0.1)
            ET.SubElement(engine, 'static-friction', attrib={"unit" : "HP"}).text = str(power_or_thrust*0.005)
            ET.SubElement(engine, 'starter-torque').text = str(power_or_thrust*0.8)
            ET.SubElement(engine, 'starter-rpm').text = "1400"

            stroke = 4.375
            bore = 5.125
            bore_s = pow(bore/2, 2.0) * 3.14159
            n_cylinders = displ / (stroke * bore_s)
            if n_cylinders < 1:
                n_cylinders = 1
            else:
                n_cylinders = floor(n_cylinders+0.5)

            ET.SubElement(engine, 'stroke', attrib={"unit" : "IN"}).text = str(4.375)
            ET.SubElement(engine, 'bore', attrib={"unit" : "IN"}).text = str(bore)
            ET.SubElement(engine, 'cylinders').text = str(n_cylinders)
            ET.SubElement(engine, 'compression_ratio').text = "8.0"

            common_functions.indent(engine)

            return engine


        elif engine_type == 'turbine':
            engine = ET.Element('turbine_engine', attrib={'name': f'{engine_name}'})
            #maxthrust = power*1.5 if afterburning : power;

            ET.SubElement(engine, 'power').text = str(power_or_thrust)
            ET.SubElement(engine, 'augmented').text = str(afterburning).lower()
            ET.SubElement(engine, 'injected').text = str(water_injection).lower()



        elif engine_type == 'turboprop':
            engine = ET.Element('turboprop_engine')
            ET.SubElement(engine, 'power').text = str(power_or_thrust)
            ET.SubElement(engine, 'units').text = str(power_unit)
            ET.SubElement(engine, 'bypassratio').text = str(0.0)
            ET.SubElement(engine, 'tsfc').text = str(0.55)
            ET.SubElement(engine, 'bleed').text = str(0.03)
            ET.SubElement(engine, 'idlen1').text = str(30.0)
            ET.SubElement(engine, 'idlen2').text = str(60.0)
            ET.SubElement(engine, 'maxn1').text = str(100.0)
            ET.SubElement(engine, 'maxn2').text= str(100.0)
            ET.SubElement(engine, 'augmented').text = str(0)
            ET.SubElement(engine, 'injected').text = str(0)

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
            engine.append(table_elem)
            engine.append(table_elem_2)

            common_functions.indent(engine)

        elif engine_type == 'rocket':
            # Roket motor XML elementi oluşturma
            engine = ET.Element('rocket_engine')
            ET.SubElement(engine, 'shr').text = str(1.23)
            ET.SubElement(engine, 'max_pc').text = str(86556)
            ET.SubElement(engine, 'variance').text = str(0.1)
            ET.SubElement(engine, 'prop_eff').text = str(0.67)
            ET.SubElement(engine, 'maxthrottle').text = str(1.0)
            ET.SubElement(engine, 'minthrottle').text = str(0.4)
            ET.SubElement(engine, 'slfuelflowmax').text = str(91.5)
            ET.SubElement(engine, 'sloxiflowmax').text = str(105.2)

            common_functions.indent(engine)

        # Motor ismi ekleme
        engine.set('name', engine_name)

        # Yorumlar ekleme
        comments = f"\n  File: {engine_name}.xml\n  Author: Aero-Matic v {version}\n\n  Inputs\n    name: {engine_type}\n    type: {engine_type}\n    power: {power_or_thrust}\n    augmented: {afterburning}\n    injected: {water_injection}\n\n"

        # XML yapısını oluşturma
        root = ET.Element("root")
        root.append(ET.Comment(comments))
        root.append(engine)
        
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
                        mime="application/xml"
                    )

if __name__ == "__main__":
    # Eğer bu dosya direkt çalıştırılırsa aşağıdaki kod çalışır.
    gener = generate()
    front = Frontend()

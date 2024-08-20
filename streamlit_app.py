import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from math import pow

version = 1.0

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

def indent(elem, level=0):
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
    return elem

def make_piston(power):
    # Piston motor XML elementi oluşturma
    engine = ET.Element('piston_engine')
    ET.SubElement(engine, 'power').text = str(power)
    return engine

def make_turbine(power, augmented, injected):
    # Türbin motor XML elementi oluşturma
    engine = ET.Element('turbine_engine')
    ET.SubElement(engine, 'power').text = str(power)
    ET.SubElement(engine, 'augmented').text = str(augmented).lower()
    ET.SubElement(engine, 'injected').text = str(injected).lower()
    return engine

def make_turboprop(power, units):
    # Turboprop motor XML elementi oluşturma
    engine = ET.Element('turboprop_engine')
    ET.SubElement(engine, 'power').text = str(power)
    ET.SubElement(engine, 'units').text = str(units)
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
        "    -10000       0   10000   20000   30000   40000   50000"
        "0.0  1.1260  1.0000  0.7400  0.5340  0.3720  0.2410  0.0\n"
        "0.2  1.1000  0.9340  0.6970  0.5060  0.3550  0.2310  0.0\n"
        "0.4  1.0000  0.6410  0.6120  0.4060  0.3570  0.2330  0.0\n"
        "0.6  0.4430  0.3510  0.2710  0.2020  0.1780  0.1020  0.0\n"
        "0.8  0.0240  0.0200  0.0160  0.0130  0.0110  0.0100  0.0\n"
        "1.0  0.0     0.0     0.0     0.0     0.0     0.0     0.0\n"
    )
    
    # Table elementini oluşturma ve veriyi ekleme
    table_elem = make_table('IdleThrust', idlethrust)
    table_elem_2 = make_table('MilThrust', milthrust)
    engine.append(table_elem)
    engine.append(table_elem_2)

    indent(engine)

    return engine

def make_rocket():
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

    indent(engine)

    return engine

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

def generate_engine(engine_name, engine_type, power_or_thrust, power_unit, afterburning, water_injection):
    # Power unit conversion
    if power_unit == 'kw':
        power_or_thrust *= 1.341
    if power_unit == 'newtons':
        power_or_thrust *= 0.2248

    # Motor türüne göre XML elementini oluşturma
    if engine_type == 'piston':
        comments += 'piston'
        engine = make_piston(power_or_thrust)
    elif engine_type == 'turbine':
        engine = make_turbine(power_or_thrust, afterburning, water_injection)
    elif engine_type == 'turboprop':
        engine = make_turboprop(power_or_thrust, power_unit)
    elif engine_type == 'rocket':
        engine = make_rocket()

    # Motor ismi ekleme
    engine.set('name', engine_name)

    # Yorumlar ekleme
    comments = f"\n  File: {engine_name}.xml\n  Author: Aero-Matic v {version}\n\n  Inputs\n    name: {engine_type}\n    type: {engine_type}\n    power: {power_or_thrust}\n    augmented: {afterburning}\n    injected: {water_injection}\n\n"

    # XML yapısını oluşturma
    root = ET.Element("root")
    root.append(ET.Comment(comments))
    root.append(engine)
    
    return root

def aircraft_set(description, pitch_offset_deg, x_offset_m, y_offset_m, z_offset_m, fdm, systems, cockpit, model_rating, tags,fuel_tanks, help_lines, help_title, previews, flight_model,model_path, audible, panelVisibility, author, aircraft_version, sound_path, aero_file, long_description, fuel_Fraction):
    set = ET.Element('sim')
    ET.SubElement(set, 'description').text = description
    ET.SubElement(set, 'long-description').text = long_description
    ET.SubElement(set, 'author').text = author
    ET.SubElement(set, 'aircraft-version').text = aircraft_version
    ET.SubElement(set, 'flight-model').text = flight_model
    ET.SubElement(set, 'aero').text = aero_file
    ET.SubElement(set, 'fuel-fraction').text = fuel_Fraction

    sound = ET.SubElement(set, "sound")
    audible_element = ET.SubElement(sound, "audible")
    audible_element.text = "true" if audible else "false"
    
    path_element = ET.SubElement(sound, "path")
    path_element.text = sound_path

    panel = ET.SubElement(set, "panel")
    ET.SubElement(panel, 'visibility').text = panelVisibility

    model = ET.SubElement(set, "model")
    ET.SubElement(model, 'path').text = model_path

    previews = ET.SubElement(set, "previews")
    prev = ET.SubElement(set, "preview")
    ET.SubElement(prev, 'type').text = 'exterior'
    ET.SubElement(prev, 'path').text = 'Previews/turkey.png'
    ET.SubElement(prev, 'splash').text = 'true'
    
    total_tag = ET.SubElement(set, "tags")
    
    dizi = tags.split()
    for i in dizi:
        ET.SubElement(total_tag, "tag").text = i

    rate = ET.SubElement(set, "rating")
    ET.SubElement(rate, 'FDM').text = str(fdm)
    ET.SubElement(rate, 'systems').text = str(systems)
    ET.SubElement(rate, 'cockpit').text = str(cockpit)
    ET.SubElement(rate, 'model').text = str(model)

    help = ET.SubElement(set, "help")
    ET.SubElement(help, 'title').text = help_title
    for j in help_lines.split("\n"):
        ET.SubElement(help, "line").text = j





    return set


def generate_set(description, pitch_offset_deg, x_offset_m, y_offset_m, z_offset_m, fdm, systems, cockpit, model_rating, tags,fuel_tanks, help_lines, help_title, previews, flight_model,model_path, audible, panelVisibility, author, aircraft_version, sound_path, aero_file, long_description, fuel_Fraction):
    
    engine = aircraft_set(description, pitch_offset_deg, x_offset_m, y_offset_m, z_offset_m, fdm, systems, cockpit, model_rating, tags,fuel_tanks, help_lines, help_title, previews, flight_model,model_path, audible, panelVisibility, author, aircraft_version, sound_path, aero_file, long_description, fuel_Fraction)

    # XML yapısını oluşturma
    root = ET.Element("PropertyList")
    root.append(engine)
    indent(root)
    
    return root

def generate_model(total_path):
    st.write(total_path)

# XML dosyasını okuyan fonksiyon
def read_xml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


#MAIN FUNCTION
def main_texts():
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


#STEPS TO ADD A AIRCRAFT
def steps():
    #STEP 1
    st.subheader("Step 1: The Engine Configuration", divider=True)
    st.write("This step is to define the engine configuration of the aircraft. Aircraft engines are critical components that provide the required thrust during flight. Elements such as engine type, power/thrust rating, fuel injection and afterburner are configured in this step. This step is required if a new engine configuration is to be created; if an existing engine configuration file is used, this step can be skipped.")
    with st.expander("**STEP :one:**"):
        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                with st.container(border=True):
                    engine_name = st.text_input("Engine Name", value="my_engine")
                    engine_type = st.radio("Engine Type", ['piston', 'turbine', 'turboprop', 'rocket'])

            with col2:
                with st.container(border=True):
                    power_or_thrust = st.text_input("Engine Power or Thrust (per engine, without afterburning)", value="1000.0")
                    power_unit = st.radio("", ['horsepower', 'kw', 'pounds', 'newtons'], index=0)

            with col3:
                with st.container(border=True):
                    afterburning = st.radio("Augmentation (afterburning) Installed?", ['yes', 'no'], index=1)
                    water_injection = st.radio("Water Injection Installed?", ['yes', 'no'], index=1)

            # Formu oluştur
            if st.button(label='Generate'):
                #engine_name,  engine_type, power_or_thrust,  power_unit,  water_injection
                # XML dosyasını oluşturma ve kaydetme
                engine_xml = generate_engine(engine_name, engine_type, power_or_thrust, power_unit, afterburning, water_injection)
                save_xml(engine_xml, f"{engine_name}.xml")
                #st.write("You are now ready to have Aeromatic generate your file. Aeromatic will create a file called `engine.php`, which is your engine configuration file. You will need to save this file with a filename of the form `engine_name.xml`.")

                xml_data = read_xml('my_engine.xml')
                st.code(xml_data, language="python", line_numbers=False)

                st.download_button(
                label="Download my_engine.xml",
                data=xml_data,
                file_name="my_engine.xml",
                mime="application/xml"
                )

    #STEP 2 
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
                st.write("Engine Name:", engine_name)
                st.write("Engine Type:", engine_type)
                st.write(f"Engine Power or Thrust: {power_or_thrust} {power_unit}")
                st.write("Augmentation (afterburning) Installed?:", afterburning)
                st.write("Water Injection Installed?:", water_injection)
                st.write("You are now ready to have Aeromatic generate your file. Aeromatic will create a file called `engine.php`, which is your engine configuration file. You will need to save this file with a filename of the form `engine_name.xml`.")

    # STEP 3
    st.subheader("Step 3: The Aero configuration ...", divider=True)
    st.write("This step is to define the aerodynamic configuration of the aircraft. Aerodynamic parameters such as wingspan, length, maximum take-off weight and landing gear layout are configured here. The overall performance, flight dynamics and stability of the aircraft are determined in this step.")
    with st.expander("**STEP :three:**"):
        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                with st.container(border=True):
                    measurement_system = st.radio("Choose a system of measurement", ['English (feet, pounds)', 'Metric (meters, kilograms)'], index=0)
                    aircraft_name = st.text_input("Name of aircraft", value="unnamed")
                    landing_gear_layout = st.radio("Landing Gear Layout", ['tricycle', 'taildragger'], index=0)
                    retractable_landing_gear = st.radio("Is the Landing Gear Retractable?", ['yes', 'no'], index=1)

            with col2:
                with st.container(border=True):
                    aircraft_type = st.radio(
                        "Type of aircraft (Select closest aerodynamic type)",
                        ['Glider', 'Light Single', 'Light Twin', 'WWII Fighter (or subsonic racer/aerobatic)',
                        'Single-engine Transonic or Supersonic Fighter', 'Two-engine Transonic or Supersonic Fighter',
                        'Two-engine Transonic Transport', 'Three-engine Transonic Transport', 'Four-engine Transonic Transport',
                        'Multi-engine Prop Transport']
                    )
                    num_engine = st.select_slider("Select a color of the rainbow",options=[str(i) for i in range(1, 9)],)
                    eng_type = st.selectbox("Engine Type", ['piston', 'turbine', 'turboprop', 'rocket'], index=0)

            with col3:
                with st.container(border=True):
                    max_takeoff_weight = st.text_input("Maximum Takeoff Weight", value="10000.0")
                    wingspan = st.text_input("Wing span", value="40.0")
                    length = st.text_input("Length", value="40.0")
                    wing_area = st.text_input("Wing area (Enter 0 to use estimated value)", value="0")

            cl1, cl2, cl3 = st.columns(3)
            with cl1:
                # Motor düzeni
                engine_layout = st.selectbox("Engine Layout", ['fwd_fuselage', 'mid_fuselage', 'aft_fuselage', 'wings', 'wings and tail', 'wings and nose'],index=0)
            
            with cl2:
                # Yaw Damper
                yaw_damper = st.radio("Yaw Damper Installed? (Almost all jets will need one)", ['yes', 'no'], index=1)

            # Formu oluştur
            if st.button("Generate 3"):
                st.write("System of Measurement:", measurement_system)
                st.write("Name of Aircraft:", aircraft_name)
                st.write("Type of Aircraft:", aircraft_type)
                st.write("Maximum Takeoff Weight:", max_takeoff_weight)
                st.write("Wing Span:", wingspan)
                st.write("Length:", length)
                st.write("Wing Area:", wing_area)
                st.write("Landing Gear Layout:", landing_gear_layout)
                st.write("Is the Landing Gear Retractable?:", retractable_landing_gear)
                st.write("Number of Engines:", num_engine)
                st.write("Engine Type:", engine_type)
                st.write("Engine Layout:", engine_layout)
                st.write("Yaw Damper Installed?:", yaw_damper)

    # STEP 4
    st.subheader("Step 4: The Thruster Configuration", divider=True)
    st.write("This step is to define the thruster configuration of the aircraft. If the aircraft has additional thruster systems, they are configured in this step. In this step, parameters such as thruster layout and power outputs are determined.") 
    with st.expander("**STEP :four:**"):
        with st.container():
            # Motor türlerini tanımla
            motor_types = ["Electric", "Piston", "Rocket", "Turbine", "TurboProp"]

            # Thruster tiplerini motor türlerine göre eşleştir
            thruster_options = {
                "Electric": ["Direct", "Propeller", "Rotor"],
                "Piston": ["Propeller", 'Rotor'],
                "Rocket": ["Nozzle"],
                "Turbine": ["Direct"],
                "TurboProp": ["Propeller", 'Rotor']
            }

            # Motor türü seçimi
            selected_motor = st.selectbox("Select Engine Type", motor_types)

            # Seçilen motor türüne göre thruster tiplerini göster
            if selected_motor:
                selected_thruster = st.selectbox("Select Thruster Type", thruster_options[selected_motor])

                if selected_thruster == "Direct":
                    st.text("No configuration required for direct thruster.")

                elif selected_thruster == "Nozzle":
                    nozzle_name = st.text_input("Nozzle Name")
                    area_unit = st.selectbox("Area Unit", ["FT2", "M2", "IN2"])
                    area = st.number_input("Nozzle Area", min_value=0.0)

                elif selected_thruster == "Propeller":
                    prop_col1, prop_col2, prop_col3 = st.columns(3)
                    with prop_col1:
                        propeller_name = st.text_input("Rotor Name", "")
                        diameter = st.number_input("Propeller disk diameter (IN)", min_value=0.0)
                        numblades = st.number_input("Number of Blades", min_value=1, value=1)
                        gearratio = st.number_input("Ratio of (engine rpm)/(prop rpm)", value=0.0)
                        nominalrpm = st.number_input("Nominal RPM", value=0.0)
                        minrpm = st.number_input("Minimum rpm target for constant speed propeller", value=1.0)
                        maxrpm = st.number_input("Maximum rpm target for constant speed propeller", value=0.0)
                        chord = st.number_input("Chord (LENGTH)", value=0.0)
                        liftcurveslope = st.number_input("Lift Curve Slope (1/RAD)", value=0.0)
                        twist = st.number_input("Twist (ANGLE)", value=0.0)
                    with prop_col2:
                        hingeoffset = st.number_input("Hinge Offset (LENGTH)", value=0.0)
                        flappingmoment = st.number_input("Flapping Moment (MOMENT)", value=0.0)
                        massmoment = st.number_input("Mass Moment (SLUG*FT)", value=0.0)
                        polarmoment = st.number_input("Polar Moment (MOMENT)", value=0.0)
                        inflowlag = st.number_input("Inflow Lag (sec)", value=0.0)
                        tiplossfactor = st.number_input("Tip Loss Factor", value=1.0)
                        maxbrakepower = st.number_input("Max Brake Power (POWER)", value=0.0)
                        controlmap = st.selectbox("Control Map", options=['MAIN', 'TAIL', 'TANDEM'])
                        externalrpm = st.number_input("External RPM", value=0.0)
                        groundeffectexp = st.number_input("Ground Effect Exponent", value=0.0)
                    with prop_col3:
                        groundeffectshift = st.number_input("Ground Effect Shift (LENGTH)", value=0.0)
                        ixx_unit = st.selectbox("İnertia Birimi", ["SLUG*FT2", "KG*M2"])
                        ixx = st.number_input("Rotational İnertia", min_value=0.0)
                        minpitch = st.number_input("Minimum blade pitch angle", min_value=0.0)
                        maxpitch = st.number_input("Maximum blade pitch angle", min_value=0.0)
                        constspeed = st.number_input("1 = constant speed mode, 0 = manual pitch mode", min_value=0, max_value=1)
                        reversepitch = st.number_input("Blade pitch angle for reverse", min_value=0.0)
                        ct_factor = st.number_input("A multiplier for the coefficients of thrust", min_value=0.0)
                        cp_factor = st.number_input("A multiplier for the coefficients of power", min_value=0.0)
                    
                    # Kullanıcıdan thrust ve power tabloları için veri iste
                    c_thrust_table = st.text_area("C_THRUST Tablosu", value="0.0   0.0580\n0.1   0.0620\n0.2   0.0600\n0.3   0.0580\n0.4   0.0520\n0.5   0.0457\n0.6   0.0436\n0.8   0.0372\n0.9   0.0299\n1.0   0.0202\n1.2   0.0075\n1.3   0.0111\n1.4   0.0202\n1.5   0.0280\n1.6   0.0346\n1.7   0.0389\n1.8   0.0421\n1.9   0.0436")
                    c_power_table = st.text_area("C_POWER Tablosu", value="                     -10         0                15                 25            35            45            55        \n-0.2      -0.0734    0.0413    0.1503    0.1842    0.2030    0.2142    0.1974    \n0.0      -0.1090    0.0000    0.1503    0.1842    0.2030    0.2162    0.2021    \n0.2      -0.1222   -0.0376    0.1297    0.1804    0.2001    0.2162    0.2021    \n0.4      -0.1222   -0.0873    0.0977    0.1786    0.1963    0.2142    0.2021    \n0.6      -0.1222   -0.1222    0.0517    0.1607    0.1879    0.2087    0.1992    \n0.8      -0.1222   -0.1222    0.0029    0.1203    0.1824    0.2012    0.1992    \n1.0      -0.1222   -0.1222   -0.0489    0.0734    0.1748    0.1908    0.1974    \n1.2      -0.1222   -0.1222   -0.1006    0.0226    0.1437    0.1842    0.1974    \n1.4      -0.1222   -0.1222   -0.1222   -0.0329    0.1034    0.1813    0.1936    \n1.8      -0.1222   -0.1222   -0.1222   -0.1222    0.0095    0.1503    0.1842    \n2.0      -0.1222   -0.1222   -0.1222   -0.1222   -0.0376    0.1174    0.1834    \n3.0      -0.1222   -0.1222   -0.1222   -0.1222   -0.1222   -0.0734    0.0320    \n4.0      -0.1222   -0.1222   -0.1222   -0.1222   -0.1222   -0.1222   -0.1137   \n6.0      -0.1222   -0.1222   -0.1222   -0.1222   -0.1222   -0.1222   -0.1222   ")
                    
                elif selected_thruster == "Rotor":
                    rotor_col1, rotor_col2, rotor_col3 = st.columns(3)
                    with rotor_col1:
                        name = st.text_input("Rotor Name", "")
                        diameter = st.number_input("Diameter (LENGTH)", value=0.0)
                        numblades = st.number_input("Number of Blades", min_value=1, value=1)
                        gearratio = st.number_input("Gear Ratio", value=0.0)
                        nominalrpm = st.number_input("Nominal RPM", value=0.0)
                        minrpm = st.number_input("Minimum RPM", value=1.0)
                        maxrpm = st.number_input("Maximum RPM", value=0.0)
                    with rotor_col2:
                        chord = st.number_input("Chord (LENGTH)", value=0.0)
                        liftcurveslope = st.number_input("Lift Curve Slope (1/RAD)", value=0.0)
                        twist = st.number_input("Twist (ANGLE)", value=0.0)
                        hingeoffset = st.number_input("Hinge Offset (LENGTH)", value=0.0)
                        flappingmoment = st.number_input("Flapping Moment (MOMENT)", value=0.0)
                        massmoment = st.number_input("Mass Moment (SLUG*FT)", value=0.0)
                        polarmoment = st.number_input("Polar Moment (MOMENT)", value=0.0)
                    with rotor_col3:    
                        inflowlag = st.number_input("Inflow Lag (sec)", value=0.0)
                        tiplossfactor = st.number_input("Tip Loss Factor", value=1.0)
                        maxbrakepower = st.number_input("Max Brake Power (POWER)", value=0.0)
                        controlmap = st.selectbox("Control Map", options=['MAIN', 'TAIL', 'TANDEM'])
                        externalrpm = st.number_input("External RPM", value=0.0)
                        groundeffectshift = st.number_input("Ground Effect Shift (LENGTH)", value=0.0)
                        groundeffectexp = st.number_input("Ground Effect Exponent", value=0.0)
    
                # Seçilen motor ve thruster türüne göre alınan verileri gösterebilirsiniz.
                if st.button("Show", type="primary", use_container_width=True):
                    st.write("Selected Engine Type:", selected_motor)
                    st.write("Selected Thruster Type:", selected_thruster)
                    if selected_thruster == "Nozzle":
                        st.write("Nozzle Adı:", nozzle_name)
                        st.write("Nozzle Alanı:", area, area_unit)
                    elif selected_thruster == "Propeller":
                        st.write("Propeller Adı:", propeller_name)
                        st.write("İnertia:", ixx, ixx_unit)
                        st.write("Disk Çapı:", diameter, "IN")
                        st.write("Bıçak Sayısı:", numblades)
                        st.write("Dişli Oranı:", gearratio)
                        st.write("Minimum Bıçak Açısı:", minpitch)
                        st.write("Maximum Bıçak Açısı:", maxpitch)
                        st.write("Minimum RPM:", minrpm)
                        st.write("Maximum RPM:", maxrpm)
                        st.write("Sabit Hız Modu:", constspeed)
                        st.write("Ters Bıçak Açısı:", reversepitch)
                        st.write("Thrust Katsayısı (Ct):", ct_factor)
                        st.write("Güç Katsayısı (Cp):", cp_factor)
                        st.write("C_THRUST Tablosu:", c_thrust_table)
                        st.write("C_POWER Tablosu:", c_power_table)
                    elif selected_thruster == "Rotor":
                        st.write("Rotor Adı:", diameter )
                        st.write("Rotor Alanı:", diameter )
                        st.write("Kuyruk Rotor:", gearratio )
                        st.write("Tandem Rotor:", numblades )
                        st.write("Dönüş Yönü (Sense):", minrpm )
                        st.write("Motor Problemleri:", twist )

    # STEP 5
    st.subheader("Step 5: Root directory aircraft-set Configuration", divider=True)
    #view, consumables, engines controls fdm eksik.
    st.write("This step defines the aircraft-set configuration file located in the root directory of the aircraft. This file contains the general description of the aircraft, its version, sound and panel settings. Also, details such as the fuel tanks used for the aircraft, model path and preview images are defined in this step.")
    with st.expander("**STEP :five:** | Root directory aircraft-set Configuration "):
        with st.container():
            #tags: description, long-description, author, aircraft-version, flight-model, aero, fuel-fraction, sound, panel, engines, fdm
            with st.container(border=True):
                    cl1, cl2, cl3 = st.columns(3)
                    with cl1:
                        description = st.text_input('Description', 'Mandalina 1.0| IDEALAB (2024)')
                    with cl2:
                        author = st.text_input('Author', 'Edip Sevincer(Manager), Selami Korkmaz(Designer)...')
                    with cl3:
                        aircraft_version = st.text_input('Aircraft Version', '1.0')

            with st.container(border=True):
                long_description = st.text_area('Long Description', 'Mandalina is an unmanned aerial vehicle produced by the IDEALAB company...')
                cl4, cl5, cl6 = st.columns(3)
                with cl4:
                    aero_file = st.text_input("Aerodynamic Model File Name", value="description")
                with cl5:
                    fuel_Fraction = st.text_input("Fuel Fraction", value="1.0 , 0.8 , 4.5")
                with cl6:
                    sound_path = st.text_input('Sound Path', 'Aircraft/Deneme/Sounds/mandalina-sound.xml')
                
            with st.container(border=True):
                cl7, cl8, cl9 = st.columns(3)
                with cl7:
                    flight_model = st.radio("Flight Model", ['JSBSim', 'YASim'], index=1)
                with cl8:
                    panelVisibility = st.radio("Aircraft Panel Visibility", ['True', 'False'], index=1)
                with cl9:
                    audible = st.radio("Sound Audible", ['True', 'False'], index=1)

            with st.container(border=True):
                model_path = st.text_input('Model Path', 'Aircraft/Deneme/Models/Deneme.xml')
                previews = st.text_area('Preview Paths', 'Previews/prev.jpg\nPreviews/prev1.jpg\n...')
                tags = st.text_area('Tags', 'high-wing\nretractable-gear\nsingle-engine\n')
                help_title = st.text_input('Help Title', 'Mandalina, Version 1.0 (IL-170)')
                help_lines = st.text_area('Help Lines', 'Cruise speed: 0.2 Mach\nNever-exceed (Vne): 0.6 Mach\n')
                fuel_tanks = st.text_area('Fuel Tanks (Format: n|name|capacity)', '0|6L-Left Tank|13.2\n1|6L-Right Tank|13.2\n')

            with st.container(border=True):
                cl10, cl11, cl12, cl13 = st.columns(4)
                with cl10:
                    fdm = st.text_input('FDM Rating', '2')
                with cl11:
                    systems = st.text_input('Systems Rating', '1')
                with cl12:
                    cockpit = st.text_input('Cockpit Rating', '0')
                with cl13:
                    model_rating = st.text_input('Model Rating', '2')

                cl14, cl15, cl16, cl17 = st.columns(4)
                with cl14:
                    x_offset_m = st.text_input('X-Offset (m)', '0.0')
                with cl15:
                    y_offset_m = st.text_input('Y-Offset (m)', '-0.3')
                with cl16:
                    z_offset_m = st.text_input('Z-Offset (m)', '0.9')
                with cl17:
                    pitch_offset_deg = st.text_input('Pitch Offset (deg)', '-8')
            
            # Formu oluştur
            if st.button(label='Generate aircraft-set.xml'):
                #engine_name,  engine_type, power_or_thrust,  power_unit,  water_injection
                # XML dosyasını oluşturma ve kaydetme
                set_xml = generate_set(description, pitch_offset_deg, x_offset_m, y_offset_m, z_offset_m, fdm, systems, cockpit, model_rating, tags,fuel_tanks, help_lines, help_title, previews, flight_model,model_path, audible, panelVisibility, author, aircraft_version, sound_path, aero_file, long_description, fuel_Fraction)
                save_xml(set_xml, f"aircraft-set.xml")
                #st.write("You are now ready to have Aeromatic generate your file. Aeromatic will create a file called `engine.php`, which is your engine configuration file. You will need to save this file with a filename of the form `engine_name.xml`.")

                xml_data = read_xml('aircraft-set.xml')
                st.code(xml_data, language="python", line_numbers=False)

                st.download_button(
                label="Download aircraft-set.xml",
                data=xml_data,
                file_name="aircraft-set.xml",
                mime="application/xml"
                )


    # STEP 6
    st.subheader("Step 6: Root directory aircraft Configuration", divider=True)
    st.write("This step defines the aircraft configuration file located in the root directory of the aircraft. This file contains the basic specifications, model information and additional features of the airplane. This step configures the paths to other files related to the aircraft and general information about the aircraft.")
    with st.expander("**STEP :six:** | Root directory aircraft Configuration"):
        with st.container():
            st.write("This is inside the container")

    # STEP 7
    st.subheader("Step 7: Models Directory Aircraft File Configuration", divider=True)
    st.write("This step defines the configuration files located in the models directory of the aircraft. These files contain the physical model of the aircraft, its moving parts (ailerons, flaps, rudders, etc.) and other visual components. This step is used to configure the visual and physical representation of the aircraft.")
    with st.expander("**STEP :seven:** | Models Directory Aircraft File Configuration"):
        with st.container():
            # Available aircraft parts
            #"Ailerons", "Elevator", "Rudder", "Flaps", "Landing Gear", "Canards", "Slats"

                        path_name = st.text_input("**.AC File Path Name**", "aircraft.ac")
                        total_data = {}
                        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Ailerons", "Elevator", "Rudder", 'Landing Gear', 'Canards', 'Flaps','Slats'])
                        with tab1:
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

                        with tab2:   
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

                        with tab3:
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

                        with tab4:
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


                        with tab5:
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

                            
                        with tab6:
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


                        with tab7: 
                            st.write("**Slats**")
                            c1, c2, c3, c4, c5 = st.columns(5)
                            with c1:
                                total_data['Slats_type'] = st.selectbox("Slats Type", ['rotate'])
                            with c2: 
                                total_data['Slats_object-name'] = st.text_input("Slats Object file name", "left_slats.079")
                            with c3: 
                                total_data['Slats_property'] = st.text_input("Slats Property", "controls/flight/aileron")
                            with c4:
                                total_data['Slats_factor'] = st.text_input("Slats Factor", "20")
                            with c5:
                                total_data['Slats_offset-deg'] = st.text_input("Slats Offset-Deg", "0")

                            c1, c2, c3, c4, c5, c6 = st.columns(6)
                            with c1:
                                total_data['Slats_x1'] = st.number_input("Slats x1 value", value=0.0, step=0.01)
                            with c2:
                                total_data['Slats_y1'] = st.number_input("Slats y1 value", value=0.0, step=0.01)
                            with c3:
                                total_data['Slats_z1'] = st.number_input("Slats z1 value", value=0.0, step=0.01)
                            with c4:
                                total_data['Slats_x2'] = st.number_input("Slats x2 value", value=0.0, step=0.01)
                            with c5:
                                total_data['Slats_y2'] = st.number_input("Slats y2 value", value=0.0, step=0.01)
                            with c6:
                                total_data['Slats_z2'] = st.number_input("Slats z2 value", value=0.0, step=0.01)



                        # Formu oluştur
                        if st.button(label='Generate set file'):
                            st.write("Olusturuldu.")
                            # XML dosyasını oluşturma ve kaydetme
                            #model_xml = generate_model(total_data)
                            #save_xml(model_xml, f"{path_name}.xml")
                            #st.write("You are now ready to have Aeromatic generate your file. Aeromatic will create a file called `engine.php`, which is your engine configuration file. You will need to save this file with a filename of the form `engine_name.xml`.")

                            #xml_data = read_xml('aircraft-set.xml')
                            #st.code(xml_data, language="python", line_numbers=False)

                            #st.download_button(
                            #label="Download aicraft-set.xml",
                            #data=xml_data,
                            #file_name="my_engine.xml",
                            #mime="application/xml")

#FOOTER FUNCTION
def footer():
    footer_col1, footer_col2 = st.columns(2)
    with footer_col1:
        st.write("You've managed to transfer your airplane to FlightGear for the first stage. Now you are on your own! You can add realism to your simulation by adding sound effects and visual customization with various aircraft liveries. The electronics and cockpit enhance the functionality of your aircraft, while thumbnails and previews enhance the visual presentation. GUI information messages and checklists will improve the user experience, while a separate menu will make your simulation more accessible. You can use FlightGear's original site for these steps. Good luck!")
        st.write("**Version 1.0**")
        st.write("*Contact me if you want to point out shortcomings or get involved in development.*", "**Tuğçe Ulucan**")
        st.image("images/turkish_flag.jpg", width=350)
    with footer_col2:
        data = pd.DataFrame({'latitude': [41.015137],'longitude': [28.979530]})
        st.map(data, zoom=10, color='#0044ff')
        



if __name__ == "__main__":
    main_texts()
    st.title("STEPS")
    with st.container(border=True):   
        steps()
    
    with st.container(border=True):   
        footer()

    

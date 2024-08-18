import streamlit as st
import pandas as pd

#MAIN 
def main_texts():
    st.set_page_config(layout="wide")
    c, cc = st.columns([0.1, 0.9])
    with c:
        logo = st.image("images/logo.png", width=100)
    with cc:
        st.title("First 5 Steps to Add Your Own Aircraft to Flightgear")

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
            if st.button("Generate"):
                st.write("Engine Name:", engine_name)
                st.write("Engine Type:", engine_type)
                st.write(f"Engine Power or Thrust: {power_or_thrust} {power_unit}")
                st.write("Augmentation (afterburning) Installed?:", afterburning)
                st.write("Water Injection Installed?:", water_injection)
                st.write("You are now ready to have Aeromatic generate your file. Aeromatic will create a file called `engine.php`, which is your engine configuration file. You will need to save this file with a filename of the form `engine_name.xml`.")

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
                tags = st.text_area('Tags', 'high-wing\nretractable-gear\nsingle-engine\n...')
                help_title = st.text_input('Help Title', 'Mandalina, Version 1.0 (IL-170)')
                help_lines = st.text_area('Help Lines', 'Cruise speed: 0.2 Mach\nNever-exceed (Vne): 0.6 Mach\n...')
                fuel_tanks = st.text_area('Fuel Tanks (Format: n|name|capacity)', '0|6L-Left Tank|13.2\n1|6L-Right Tank|13.2\n...')

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
            
            submit_button = st.button(label='Generate XML')

            if submit_button:
                st.write('Form submitted successfully!')
                # Burada formdan alınan verilerle XML dosyası oluşturulabilir.


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
                    available_parts = [
                "Ailerons", "Elevator", "Rudder", "Flaps", "Spoilers", "Landing Gear",
                "Canards", "Slats", "Airbrakes/Spoilers", "Specialized Control Surfaces",
                "Propellers", "Thrust Vectoring Nozzles"
            ]

            # Step 1: Select which movable parts to configure
            #selected_parts = st.multiselect("Select movable parts to configure", available_parts)

            #if st.button("Continue with inputs"):
                #if 'Ailerons' in selected_parts:
                    hor1, hor2 = st.columns(2)
                    with hor1:
                        with st.container(border=True):
                            st.write("**Ailerons**")
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                x1_a = st.number_input("Enter x1_a value", value=0.0, step=0.01)
                            with c2:
                                y1_a = st.number_input("Enter y1-a value", value=0.0, step=0.01)
                            with c3:
                                z1_a = st.number_input("Enter z1-a value", value=0.0, step=0.01)
                            
                            st.write("**Elevator**")
                            c4, c5, c6  = st.columns(3)
                            with c4:
                                x1_e = st.number_input("Enter x1-m value", value=0.0, step=0.01)
                            with c5:
                                y1_e = st.number_input("Enter y1-m value", value=0.0, step=0.01)
                            with c6:
                                z1_e = st.number_input("Enter z1-m value", value=0.0, step=0.01)

                            st.write("**Spoilers**")
                            c14, c15, c16 = st.columns(3)
                            with c14:
                                x1_s = st.number_input("Enter x1-s value", value=0.0, step=0.01)
                            with c15:
                                y1_s = st.number_input("Enter y1-s value", value=0.0, step=0.01)
                            with c16:
                                z1_s = st.number_input("Enter z1-s value", value=0.0, step=0.01)

                            st.write("**Canards**")
                            c20, c21, c22 = st.columns(3)
                            with c20:
                                x1_c = st.number_input("Enter x1-c value", value=0.0, step=0.01)
                            with c21:
                                y1_c = st.number_input("Enter y1-c value", value=0.0, step=0.01)
                            with c22:
                                z1_c = st.number_input("Enter z1-c value", value=0.0, step=0.01)
                    
                    with hor2:
                        with st.container(border=True):
                            st.write("**Rudder**")
                            c7, c8, c9 = st.columns(3)
                            with c7:
                                x1_r = st.number_input("Enter x1-r value", value=0.0, step=0.01)
                            with c8:
                                y1_r = st.number_input("Enter y1-r value", value=0.0, step=0.01)
                            with c9:
                                z1_r = st.number_input("Enter z1-r value", value=0.0, step=0.01)

                            st.write("**Flaps**")
                            c10, c11, c12 = st.columns(3)
                            with c10:
                                x1_f = st.number_input("Enter x1-f value", value=0.0, step=0.01)
                            with c11:
                                y1_f = st.number_input("Enter y1-f value", value=0.0, step=0.01)
                            with c12:
                                z1_f = st.number_input("Enter z1-f value", value=0.0, step=0.01)

                            st.write("**Landing Gear**")
                            c17, c18, c19 = st.columns(3)
                            with c17:
                                x1_l = st.number_input("Enter x1-l value", value=0.0, step=0.01)
                            with c18:
                                y1_l = st.number_input("Enter y1-l value", value=0.0, step=0.01)
                            with c19:
                                z1_l = st.number_input("Enter z1-l value", value=0.0, step=0.01)

                            st.write("**Slats**")
                            c23, c24, c25 = st.columns(3)
                            with c23:
                                x1_sl = st.number_input("Enter x1-sl value", value=0.0, step=0.01)
                            with c24:
                                y1_sl = st.number_input("Enter y1-sl value", value=0.0, step=0.01)
                            with c25:
                                z1_sl = st.number_input("Enter z1-sl value", value=0.0, step=0.01)

                            axis7 = {"x1-m": x1_sl, "y1-m": y1_sl, "z1-m": z1_sl}


                    axis = {"x1-m": x1_a, "y1-m": y1_a, "z1-m": z1_a}
                    axis2 = {"x1-m": x1_e, "y1-m": y1_e, "z1-m": z1_e}
                    axis3 = {"x1-m": x1_r, "y1-m": y1_r, "z1-m": z1_r}
                    axis4 = {"x1-m": x1_f, "y1-m": y1_f, "z1-m": z1_f}
                    axis5 = {"x1-m": x1_s, "y1-m": y1_s, "z1-m": z1_s}
                    axis6 = {"x1-m": x1_l, "y1-m": y1_l, "z1-m": z1_l}
                    axis7 = {"x1-m": x1_c, "y1-m": y1_c, "z1-m": z1_c}


                    if st.button("Parameters Ready!"):
                        st.write(axis, axis2, axis3, axis4, axis5, axis6, axis7)
    
    # STEP 8
    st.subheader("Step 8", divider=True)
    st.write("This is inside the container")
    with st.expander("**STEP :eight:**"):
        with st.container():
            st.subheader("Step 8", divider=True)
            st.write("This is inside the container")

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
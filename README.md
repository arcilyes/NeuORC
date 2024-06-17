# **NeuORC Preliminary Organic Rankine Cycle Calculator README**

**Welcome to the NeuORC program's GitHub repository!**  
This program is designed as an educational tool for understanding and applying the principles of the Organic Rankine Cycle (ORC) for power generation through waste heat recovery and geothermal energy applications.  
ORC systems can be calculated simply by using the 124 fluids in the CoolProp library.  
Developed using Python, this software aims to provide an intuitive learning experience through a user-friendly graphical interface.

## **Getting Started:**
- Clone the repository to your local machine or download the latest release compatible with your system.
- Ensure Python is installed.
- Ensure the CoolProp and wxPython libraries are installed.
- Run the main script to launch the GUI and explore the functionalities.

## **Usage:**
- Navigate through the GUI to learn about ORC components and their operations.
- The program requires nine thermal and six economic inputs in order to calculate. All text boxes must be filled out before applying the calculation.
- This tool is intended for educational purposes, providing a hands-on approach to learning about ORC systems.

For more details, refer to the documentation included in the repository. **Happy learning!**

## **Dependencies:**
- CoolProp==6.6.0
- matplotlib==3.7.0
- numpy==1.24.2
- wxPython==4.2.0

## **Assumptions:**
- Heat source and cooling flow fluids are assumed to be "water.". This can be modified in code, but not in the GUI.
- Ambient temperature is taken as 25 °C; if you put lower temperatures for cooling flow, negative values will be calculated for exergy efficiencies. 
## **Screenshot:**
![image](https://github.com/arcilyes/NeuORC/assets/68187936/dc384297-7adc-4295-99d6-1635dd2547f2)


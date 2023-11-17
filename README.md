# EEDIPy
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
[![Gmail][mail-shield]][mail-url]
> EEDIPy is a python implementation of the EEDI calculation

## Table of Contents
* [General Info](#general-information)
* [Setup](#setup)
* [Usage](#usage)
* [Verification](#verification)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)

## General Information
- This project is intended to help the industry with a more accessible method to calculate the EEDI of a ship.
It is not intended to replace any industry services for EEDI verification.
- EEDI is a complicated calculatin by its very nature. The motivation is to provide an easy to use framework to remove to complexity.


## Setup
The project has been developed with Python 3.11. Other Python versions have not been verified.

Clone the repo and install the full list of dependancies are provided in the file requirements.txt. It is recommended to create a standard virtual environment with Python 3.11 and requirements.txt.


## Usage
The code is presented in the Jupyter Notebook "eedipy.ipynb" with a corresponding input Microsoft Excel sheet, "inputs.xlsx". The ship parameters are input to "inputs.txt" and the whole notebook should be run. Outputs are presented in-line at the end of the notebook (Section marked "Final EEDI" and onwards).

Numerous examples are provided in the folders "verification" and "examples". They can be run by un-commenting out the relevant lines in the "Verification" section of the notebook


```
### Verification

#un-comment verifications you want to run
#mepc 79
# inpt = pd.read_excel(homepath + 'verifications/mepc_79_1.xlsx')
# inpt = pd.read_excel(homepath + 'verifications/mepc_79_2.xlsx')

```

## Verification
The code outputs have been verified against:
- [MEPC.364(79) Appendix 4](https://wwwcdn.imo.org/localresources/en/KnowledgeCentre/IndexofIMOResolutions/MEPCDocuments/MEPC.364(79).pdf)
- [IACS PR 38 Rev4 Section 6.5 and Appendix 6](https://iacs.org.uk/resolutions/procedural-requirements/31-41/pr-38-rev3-cln)

## Project Status
Project is:  _active_



## Room for Improvement
This tool is still in its early stages. All feedback is welcomed in all areas

To do list:
- Create more comprehensive user guide
- Create web app instead of Jupyter Notebook


## Contact
Created by Mike W. - feel free to contact me!

[mail-shield]: https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white
[mail-url]: mailto:EEDIPy.project@gmail.com
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white
[linkedin-url]: https://www.linkedin.com/in/mike-wilson14/



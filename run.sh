#!/bin/bash

# Default values
eta=1
beta=0.001
lateburst=false
agb_fraction=0.2
out_of_box_agb=false
agb_model="C11"
lateburst_amplitude=1.5
fe_ia_factor="None"
filename=""
dt=0.01
Nstars=2
alpha_n=0.5
y_c_cc_0=0.0028


function display_help {
  echo "Usage: $0 [OPTIONS]"
  echo "Options:"
  echo "  -e, --eta              the efficiency multiplier of the supernova feedback (default: 1)"
  echo "  -b, --beta             the power-law index of the star formation law (default: 0.001)"
  echo "  -l, --lateburst        add a late burst of star formation (default: false)"
  echo "  -f, --agb_fraction     the mass fraction of AGB stars in the initial mass function (default: 0.2)"
  echo "  -o, --out_of_box_agb   use an out-of-box AGB model (default: false)"
  echo "  -m, --agb_model        the name of the AGB model to use (default: C11)"
  echo "  -n, --filename         the name of the output file (default: auto-generated)"
  echo "  -A, --lateburst_amplitude   the amplitude of the late burst (default: 1.5)"
  echo "  -i, --fe_ia_factor     the iron yield factor of type Ia supernovae (default: none)"
  echo "  -d, --timestep         the size of the time step (default: 0.01)"
  echo "  -a, --alpha_n          the agb fraction of primary N"
  echo "  -p, --c_plateau        the amount of plateau carbon"
  echo "  -h, --help             display this help message"
}


# Function to generate filename
function generate_filename {
  # Extract command line arguments
  local eta="$1"
  local beta="$2"
  local lateburst="$3"
  local agb_fraction="$4"
  local out_of_box_agb="$5"
  local agb_model="$6"
  local lateburst_amplitude="$7"
  local fe_ia_factor="$8"
  local dt="$9"

  # Generate filename
  local filename="${agb_model}_f${agb_fraction}"
  if [ "$out_of_box_agb" = true ]; then
    filename="${filename}_OOB"
  fi
  filename="${filename}_eta${eta}_beta${beta}"
  if [ "$lateburst" = true ]; then
    filename="${filename}_lateburst${lateburst_amplitude}"
  fi
  if [ "$fe_ia_factor" != "None" ]; then
    filename="${filename}_Fe${fe_ia_factor}"
  fi
  if [ "$dt" != 0.01 ]; then
    filename="${filename}_dt${dt}"
  fi
  if [ "$alpha_n" != 0.5 ]; then
    filename="${filename}_an${alpha_n}"
  fi
  if [ "$y_c_cc_0" != 0.0028 ]; then
    filename="${filename}_p${y_c_cc_0}"
  fi
  filename="${filename}"

  # Return filename
  echo "$filename"
}


while [[ $# -gt 0 ]]
do
  key="$1"
  case $key in
    -e|--eta)
      eta="$2"
      shift
      shift
      ;;
    -b|--beta)
      beta="$2"
      shift
      shift
      ;;
    -l|--lateburst)
      lateburst=true
      shift
      ;;
    -f|--agb_fraction)
      agb_fraction="$2"
      shift
      shift
      ;;
    -o|--out_of_box_agb)
      out_of_box_agb=true
      shift
      ;;
    -m|--agb_model)
      agb_model="$2"
      shift
      shift
      ;;
    -n|--filename)
      filename="$2"
      shift
      shift
      ;;
    -A|--lateburst_amplitude)
      lateburst_amplitude="$2"
      shift
      shift
      ;;
    -i|--fe_ia_factor)
      fe_ia_factor="$2"
      shift
      shift
      ;;
    -d|--timestep)
      dt="$2"
      shift
      shift
      ;;
    -N|--Nstars)
      Nstars="$2"
      shift
      shift
      ;;
    -a|--alpha_n)
      alpha_n="$2"
      shift
      shift
      ;;
    -p|--c_plateau)
      y_c_cc_0="$2"
      shift
      shift
      ;;
    -h|--help)
      display_help
      exit 0
      ;;
    *)
      echo "Unknown option: $key"
      exit 1
      ;;
  esac
done

# Generate filename
if [ "$filename" = "" ]; then
    filename=$(generate_filename "$eta" "$beta" "$lateburst" "$agb_fraction" "$out_of_box_agb" "$agb_model" "$lateburst_amplitude" "$fe_ia_factor" "$dt")
fi

echo "Filename: $filename"

# create call to python script
read -r -d '' pycall << EOT
from surp.osc.simulate import main
import sys
true = True
false = False

path=sys.argv[1]
main(path, '${filename}',
     eta=${eta}, 
     beta=${beta}, 
     lateburst=${lateburst},
     f_agb=${agb_fraction},
     OOB=${out_of_box_agb},
     agb_model='${agb_model}',
     A=${lateburst_amplitude},
     fe_ia_factor=${fe_ia_factor},
     dt=${dt},
     n_stars=${Nstars},
     alpha_n=${alpha_n},
     y_c_cc_0=${y_c_cc_0}
    )
EOT

echo "$pycall"

# Pass arguments to Python script
bash osc/simulate.sh "$filename" "$pycall"
# Exit with success
exit 0
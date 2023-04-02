#!/bin/bash

# Default values
eta=1
beta=0.001
lateburst=false
agb_fraction=0.2
out_of_box_agb=false
agb_model="C11"
lateburst_amplitude=1.5
fe_ia_factor=""
filename=""

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

  # Generate filename
  local filename="${agb_model}_f${agb_fraction}"
  if [ "$out_of_box_agb" = true ]; then
    filename="${filename}_OOB"
  fi
  filename="${filename}_eta${eta}_beta${beta}"
  if [ "$lateburst" = true ]; then
    filename="${filename}_lateburst${lateburst_amplitude}"
  fi
  if [ "$fe_ia_factor" != "" ]; then
    filename="${filename}_Fe${fe_ia_factor}"
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
    filename=$(generate_filename "$eta" "$beta" "$lateburst" "$agb_fraction" "$out_of_box_agb" "$agb_model" "$lateburst_amplitude" "$fe_ia_factor")
fi

# Do something with the generated filename...
echo "Filename: $filename"


# Pass arguments to Python script
bash osc/simulate.sh "$filename" \
  --eta "$eta" \
  --beta "$beta" \
  $(if [ "$lateburst" = true ]; then echo "--lateburst"; fi) \
  --agb_fraction "$agb_fraction" \
  $(if [ "$out_of_box_agb" = true ]; then echo "--out_of_box_agb"; fi) \
  --agb_model "$agb_model" \
  --lateburst_amplitude "$lateburst_amplitude" \
  $(if [ "$fe_ia_factor" != "" ]; then echo "--fe_ia_factor $fe_ia_factor"; fi) \
  $(if [ "$traditional_f" = false ]; then echo "--no_traditional_f"; fi)

# Exit with success
exit 0

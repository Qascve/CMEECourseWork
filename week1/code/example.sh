echo "Remove    excess      spaces." | tr -s " "
echo "removeb allb theb b's bbbbbb" | tr -d "b"
echo "set to uppercase" | tr [:lower:] [:upper:]
echo "only keep numbers 1O.33 10.33 1.33" | tr -d [:alpha:] | tr -s " " ","
#!/bin/sh

## Illustrates the use of variables 

# Special variables

echo "This script was called with $# parameters"
echo "The script's name is $0"
echo "The arguments are $@"
echo "The first argument is $1"
echo "The second argument is $2"

# Assigned Variables; Explicit declaration:
MY_VAR='learning shell scripting is not fun!' 
echo 'the current value of the variable is:' $MY_VAR
echo #space line
echo 'Please enter a new string'
read MY_VAR
echo

if [ $# -eq 0 ]; then # Check if any arguments are provided
    echo "Error: No input provided"
    exit 1
fi

echo 'the current value of the variable is:' $MY_VAR
echo #space line

## Assigned Variables; Reading (multiple values) from user input:
echo 'Enter two numbers separated by space(s)'
read a b

if [ $# -eq 0 ]; then # Check if any arguments are provided
    echo "Error: No input provided"
    exit 1
fi

echo #space line
echo 'you entered' $a 'and' $b '; Their sum is:'

## Assigned Variables; Command substitution
MY_SUM=$(expr $a + $b)
echo $MY_SUM
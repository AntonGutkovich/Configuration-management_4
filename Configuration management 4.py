import argparse
import struct
import csv

result_data = []
log_file_data = []

def parse_args():
    parser = argparse.ArgumentParser(description="Assembler and Interpreter for UVM")
    parser.add_argument("mode", choices=["assemble", "interpret"], help="Operation mode: 'assemble' or 'interpret'")
    parser.add_argument("input_file", help="Input file")
    parser.add_argument("output_file", help="Output file")
    parser.add_argument("log_file", help="Log file (CSV format)")
    parser.add_argument("--result_file", help="Result file for interpreter (CSV format)")
    parser.add_argument("--memory_range", help="Memory range for interpreter (start:end)", type=str)
    return parser.parse_args()

def read_input_file(input_file):
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Error! File {input_file} not found")
        exit(1)

def parse_instruction(instruction):
    parts = instruction.split(',')
    values = {}
    for part in parts:
        key, value = part.split('=')
        values[key.strip()] = int(value.strip())
    return values

def assemble_instruction(value):
    global result_data, log_file_data
    A = value['A']

    try:
        B = value['B']
        instruction = bytearray()

        if A in {120, 36, 51}: 
            instruction.append(A)

            if A in {120, 36}:  
                instruction.extend(struct.pack(">I", B))
            elif A == 51:  
                instruction.extend(struct.pack(">I", B))

        result_data.extend(instruction)

        log_file_data.append({
            "A": A,
            "B": B,
            "instruction": ','.join(hex(byte) for byte in instruction)
        })

    except KeyError:
        print("Error! Missing parameters in instruction")
        exit(1)

def write_log_file(log_file):
    with open(log_file, 'w', newline='') as csvfile:
        fieldnames = ['A', 'B', 'instruction']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for entry in log_file_data:
            writer.writerow(entry)

    print(f"Log written to {log_file}")

def write_binary_file(output_file):
    with open(output_file, "wb") as file:
        file.write(bytearray(result_data))
    print(f"Binary written to {output_file}")

def read_binary_file(input_file):
    try:
        with open(input_file, "rb") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error! File {input_file} not found")
        exit(1)

def interpret_commands(binary_data, memory_range):
    memory = [0] * 1024 
    accumulator = 0
    for i in range(0, len(binary_data)):
        A = binary_data[i]
        if A == 120:  
            i += 1
            B = struct.unpack(">I", binary_data[i:i+4])[0]
            accumulator = B
        elif A == 101: 
            accumulator = memory[accumulator]
        elif A == 36:  
            i += 1
            B = struct.unpack(">I", binary_data[i:i+4])[0]
            memory[B] = accumulator
        elif A == 51:  
            i += 1
            B = struct.unpack(">I", binary_data[i:i+4])[0]
            memory[B] = 1 if memory[B] != accumulator else 0

    start, end = map(int, memory_range.split(":"))
    return memory[start:end]

def write_result_file(result_file, memory_slice):
    with open(result_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Address', 'Value'])
        for address, value in enumerate(memory_slice):
            writer.writerow([address, value])
    print(f"Result written to {result_file}")

def main():
    args = parse_args()
    if args.mode == "assemble":
        instructions = read_input_file(args.input_file)
        for line in instructions:
            if not line.strip():
                continue
            values = parse_instruction(line.strip())
            assemble_instruction(values)
        write_binary_file(args.output_file)
        write_log_file(args.log_file)
    elif args.mode == "interpret":
        if not args.result_file or not args.memory_range:
            print("Error! Result file and memory range are required for interpretation.")
            exit(1)
        binary_data = read_binary_file(args.input_file)
        memory_slice = interpret_commands(binary_data, args.memory_range)
        write_result_file(args.result_file, memory_slice)

if __name__ == "__main__":
    main()


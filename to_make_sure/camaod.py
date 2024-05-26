def create_numbers_file(file_path, start, end):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for number in range(start, end + 1):
                file.write(f"{number}\n")
        print(f"File '{file_path}' created successfully with numbers from {start} to {end}.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
file_path = '../text_send.txt'
create_numbers_file(file_path, 1, 700000*2)


# if 1 in [1,2,3]:
#     print("shalom")
#
import argparse
from pathlib import Path
from rembg import remove, new_session

def remove_background(input_path: Path, output_path: Path):
    model_name = "u2netp"
    session = new_session(model_name)
    print(f"processing: {input_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(input_path, 'rb') as i:
            with open(output_path, 'wb') as o:
                input_data = i.read()
                output_data = remove(input_data, session=session)
                o.write(output_data)
        print(f"saved to: {output_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="image processing tool")
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="input path"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="output path"
    )
    args = parser.parse_args()

    input_file = Path(args.input)
    output_file = Path(args.output)

    if not input_file.exists():
        print(f"Error: file doesn't exist -> {input_file}")
    else:
        remove_background(input_file, output_file)

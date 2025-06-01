import json
import tempfile
import subprocess

def extract_and_execute(json_response: str):
    try:
        data = json.loads(json_response)
        answer = data.get("answer", "")
        python_code = data.get("python_code", "")

        if python_code:
            # Don't decode with unicode_escape
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
                temp_file.write(python_code)
                temp_path = temp_file.name

            subprocess.run(["python", temp_path], check=True)

        return "Sucessfully compleated the task"

    except json.JSONDecodeError as e:
        return "There was a error occured while i was performing the task. please try again"
    except subprocess.CalledProcessError as e:
        return "There was a error occured while i was performing the task. please try again"
    except:
        return "There was a error occured while i was performing the task. please try again"

# json_input = {
#   "answer": "Yes, I will sign the 'Internship Letter - Vineet Gupta (1).pdf' using the 'signature.png' from this folder.",
#   "python_code": "import fitz  # PyMuPDF\nfrom PIL import Image\n\n# Paths\npdf_path = 'C://Users//KIIT//Desktop//Folder//test-personal assistant//Internship Letter - Vineet Gupta (1).pdf'\nsignature_path = 'C://Users//KIIT//Desktop//Folder//test-personal assistant//signature.png'\noutput_pdf_path = 'C://Users//KIIT//Desktop//Folder//test-personal assistant//Internship Letter - Vineet Gupta (Signed).pdf'\n\n# Open the signature image and resize\nsignature_img = Image.open(signature_path)\nsignature_width, signature_height = 150, 60\nsignature_img = signature_img.resize((signature_width, signature_height))\nsignature_img.save('temp_signature.png')\n\n# Open PDF\npdf = fitz.open(pdf_path)\npage = pdf[0]\n\n# Set position for the signature (bottom right corner)\nrect = fitz.Rect(page.rect.width - signature_width - 72, \n                72, \n                page.rect.width - 72, \n                72 + signature_height)\n\n# Insert signature\npage.insert_image(rect, filename='temp_signature.png')\n\n# Save output\npdf.save(output_pdf_path)\npdf.close()\nimport os\nos.remove('temp_signature.png')"
# }


# print(extract_and_execute(json.dumps(json_input)))




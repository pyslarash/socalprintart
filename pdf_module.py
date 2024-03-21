from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import docx.oxml.shared  # Add this import for OxmlElement
import docx.text.run  # Add this import for Run
from docx2pdf import convert
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

step_three_folder = os.getenv('STEP_THREE_FOLDER')

def add_hyperlink(paragraph, text, url):
    # This gets access to the document.xml.rels file and gets a new relation id value
    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)

    # Create the w:hyperlink tag and add needed values
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id, )

    # Create a new run object (a wrapper over a 'w:r' element)
    new_run = docx.text.run.Run(
        docx.oxml.shared.OxmlElement('w:r'), paragraph)
    new_run.text = text

    # Set the run's style to the builtin hyperlink style, defining it if necessary
    new_run.style = get_or_create_hyperlink_style(part.document)

    # Join all the xml elements together
    hyperlink.append(new_run._element)
    paragraph._p.append(hyperlink)
    return hyperlink

def get_or_create_hyperlink_style(d):
    if "Hyperlink" not in d.styles:
        if "Default Character Font" not in d.styles:
            ds = d.styles.add_style("Default Character Font",
                                    docx.enum.style.WD_STYLE_TYPE.CHARACTER,
                                    True)
            ds.element.set(docx.oxml.shared.qn('w:default'), "1")
            ds.priority = 1
            ds.hidden = True
            ds.unhide_when_used = True
            del ds
        hs = d.styles.add_style("Hyperlink",
                                docx.enum.style.WD_STYLE_TYPE.CHARACTER,
                                True)
        hs.base_style = d.styles["Default Character Font"]
        hs.unhide_when_used = True
        hs.font.color.rgb = docx.shared.RGBColor(0x05, 0x63, 0xC1)
        hs.font.underline = True
        hs.font.name = 'Libre Baskerville'  # Set font name to Libre Baskerville
        del hs

    return "Hyperlink"

def insert_link_after_paragraph(date_folder, generated_name):
    doc = Document("thank_you.docx")
    
    # Insert an empty paragraph after the last paragraph
    p = doc.add_paragraph()

    # Set paragraph properties
    p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    p.style.font.size = Pt(11)
    
    link_url="https://socalprint.art/" + date_folder + "/" + generated_name + ".zip"

    # Add the hyperlink
    add_hyperlink(p, "Click here to download", link_url)
    
    doc_name = generated_name + ".docx"
    
    output_folder = os.path.join(step_three_folder, date_folder, "pdf")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_file = os.path.join(output_folder, doc_name)

    # Save the modified document
    doc.save(output_file)

    # Convert DOCX to PDF
    convert(output_file)
    
    # Delete the output DOCX file
    os.remove(output_file)

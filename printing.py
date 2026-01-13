#from comtypes import client

def convert_docx_to_pdf(docx: str, pdf: str):
    """ docx is path to input word document | pdf is path to output pdf document """
    word = None#client.CreateObject("Word.Application")
    word.Visible = False
    doc = word.Documents.Open(docx)
    doc.SaveAs(pdf, FileFormat=17)
    doc.Close()
    word.Quit()

"""
معالج PDF محسّن مع دعم OCR للملفات الممسوحة ضوئياً
✅ يدعم استخراج النص من PDF العادي
✅ يدعم OCR للملفات الممسوحة ضوئياً
✅ يدعم العربية والإنجليزية
"""

import pdfplumber
import PyPDF2
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import os

# للـ OCR
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ مكتبات OCR غير مثبتة. سيتم تخطي معالجة الملفات الممسوحة.")

# *******************************************************************
# تثبيت المكتبات:
# pip install pdfplumber PyPDF2 fpdf2 arabic-reshaper python-bidi
# pip install pdf2image pytesseract pillow
# 
# تحميل Tesseract OCR:
# https://github.com/UB-Mannheim/tesseract/wiki
# بعد التثبيت، حدث المسار أدناه
# *******************************************************************

# ⚙️ إعدادات Tesseract (غيّر المسار حسب التثبيت عندك)
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_text_with_pdfplumber(file_path):
    """استخراج النص باستخدام pdfplumber"""
    texts = []
    print(f"📖 محاولة القراءة باستخدام pdfplumber...")
    
    with pdfplumber.open(file_path) as pdf:
        print(f"   عدد الصفحات: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                texts.append(text.strip())
                print(f"   ✅ تم استخراج النص من الصفحة {i+1}")
            else:
                texts.append("")
                print(f"   ⚠️ الصفحة {i+1} فارغة")
    
    return texts


def extract_text_with_pypdf2(file_path):
    """استخراج النص باستخدام PyPDF2"""
    texts = []
    print(f"📖 محاولة القراءة باستخدام PyPDF2...")
    
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        print(f"   عدد الصفحات: {len(pdf_reader.pages)}")
        
        for i, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            if text and text.strip():
                texts.append(text.strip())
                print(f"   ✅ تم استخراج النص من الصفحة {i+1}")
            else:
                texts.append("")
                print(f"   ⚠️ الصفحة {i+1} فارغة")
    
    return texts


def extract_text_with_ocr(file_path, lang='eng'):
    """
    استخراج النص من PDF ممسوح ضوئياً باستخدام OCR
    lang: 'eng' للإنجليزية، 'ara' للعربية، 'eng+ara' للاثنين
    """
    if not OCR_AVAILABLE:
        raise Exception("مكتبات OCR غير مثبتة")
    
    print(f"🔍 محاولة استخراج النص باستخدام OCR (اللغة: {lang})...")
    
    try:
        # تعيين مسار Tesseract
        if os.path.exists(TESSERACT_PATH):
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        
        # تحويل PDF لصور
        print(f"   📸 تحويل PDF إلى صور...")
        images = convert_from_path(file_path, dpi=300)
        print(f"   ✅ تم تحويل {len(images)} صفحة")
        
        texts = []
        for i, image in enumerate(images):
            print(f"   🔍 معالجة الصفحة {i+1} بـ OCR...")
            
            # استخراج النص من الصورة
            text = pytesseract.image_to_string(image, lang=lang)
            
            if text and text.strip():
                texts.append(text.strip())
                print(f"   ✅ تم استخراج {len(text)} حرف من الصفحة {i+1}")
            else:
                texts.append("")
                print(f"   ⚠️ لم يتم العثور على نص في الصفحة {i+1}")
        
        return texts
        
    except Exception as e:
        print(f"   ❌ فشل OCR: {str(e)}")
        raise


def extract_text_from_pdf(file_path, use_ocr=False, ocr_lang='eng'):
    """
    استخراج النص من PDF مع محاولة طرق متعددة
    use_ocr: إذا True، يستخدم OCR مباشرة
    ocr_lang: لغة OCR ('eng', 'ara', 'eng+ara')
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ الملف غير موجود: {file_path}")
        
        print(f"\n{'='*60}")
        print(f"📄 معالجة الملف: {os.path.basename(file_path)}")
        print(f"📍 المسار الكامل: {file_path}")
        print(f"📊 حجم الملف: {os.path.getsize(file_path) / 1024:.2f} KB")
        print(f"{'='*60}\n")
        
        texts = []
        
        # إذا طلب OCR مباشرة
        if use_ocr:
            if OCR_AVAILABLE:
                return extract_text_with_ocr(file_path, ocr_lang)
            else:
                print("❌ OCR غير متوفر. جرب الطرق العادية...")
        
        # المحاولة 1: pdfplumber
        try:
            texts = extract_text_with_pdfplumber(file_path)
            if texts and any(t.strip() for t in texts):
                print(f"\n✅ نجحت القراءة باستخدام pdfplumber")
                return texts
        except Exception as e:
            print(f"\n⚠️ فشلت pdfplumber: {str(e)}")
        
        # المحاولة 2: PyPDF2
        try:
            texts = extract_text_with_pypdf2(file_path)
            if texts and any(t.strip() for t in texts):
                print(f"\n✅ نجحت القراءة باستخدام PyPDF2")
                return texts
        except Exception as e:
            print(f"\n⚠️ فشلت PyPDF2: {str(e)}")
        
        # المحاولة 3: OCR تلقائي للملفات الفارغة
        if not texts or all(not t.strip() for t in texts):
            print(f"\n🔍 الملف يبدو أنه ممسوح ضوئياً. محاولة OCR...")
            
            if OCR_AVAILABLE:
                try:
                    texts = extract_text_with_ocr(file_path, ocr_lang)
                    if texts and any(t.strip() for t in texts):
                        print(f"\n✅ نجح OCR!")
                        return texts
                except Exception as e:
                    print(f"\n❌ فشل OCR: {str(e)}")
            else:
                print("\n❌ OCR غير متوفر. يجب تثبيت:")
                print("   pip install pdf2image pytesseract pillow")
                print("   وتحميل Tesseract من:")
                print("   https://github.com/UB-Mannheim/tesseract/wiki")
        
        if not texts or all(not t.strip() for t in texts):
            raise Exception("لم يتم استخراج أي نص من الملف")
        
        return texts
    
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        raise
    except Exception as e:
        print(f"\n❌ خطأ في قراءة PDF: {e}")
        print(f"\n💡 نصائح:")
        print(f"   1. إذا كان الملف ممسوح ضوئياً، ثبت OCR")
        print(f"   2. تأكد من أن الملف ليس محمياً")
        print(f"   3. تأكد من أن الملف ليس تالفاً")
        print(f"   4. جرب فتح الملف بقارئ PDF")
        raise


def create_pdf(texts, output_path):
    """إنشاء PDF بالعربية باستخدام FPDF"""
    try:
        print(f"\n{'='*60}")
        print(f"📝 إنشاء ملف PDF جديد...")
        print(f"{'='*60}\n")
        
        pdf = FPDF()
        
        # محاولة إضافة خط عربي
        try:
            font_path = "C:/Windows/Fonts/arial.ttf"
            font_name = 'ArialUnicode'
            
            if os.path.exists(font_path):
                pdf.add_font(font_name, '', font_path, uni=True)
                pdf.set_font(font_name, '', 12)
                print("✅ تم تحميل خط Arial Unicode")
            else:
                print("⚠️ استخدام الخط الافتراضي")
                pdf.set_font('Arial', '', 12)
        
        except Exception as font_error:
            print(f"⚠️ تحذير: {font_error}")
            pdf.set_font('Arial', '', 12)
        
        # إضافة الصفحات
        for i, page_text in enumerate(texts):
            pdf.add_page()
            print(f"📄 معالجة الصفحة {i+1}...")
            
            if not page_text.strip():
                continue
            
            # تحويل النص العربي
            try:
                reshaped_text = reshape(page_text)
                bidi_text = get_display(reshaped_text)
            except Exception:
                bidi_text = page_text
            
            # كتابة الفقرات
            paragraphs = bidi_text.split('\n')
            
            for para in paragraphs:
                if para.strip():
                    try:
                        pdf.multi_cell(0, 10, para, align='R')
                    except Exception:
                        continue
                else:
                    pdf.ln(5)
        
        pdf.output(output_path)
        print(f"\n✅ تم إنشاء الملف: {output_path}")
        print(f"📊 حجم الملف: {os.path.getsize(output_path) / 1024:.2f} KB\n")
        
        return output_path
    
    except Exception as e:
        print(f"\n❌ خطأ في إنشاء PDF: {str(e)}")
        raise


def process_pdf_file(input_path, output_path, use_ocr=False, ocr_lang='eng'):
    """
    معالجة ملف PDF
    use_ocr: استخدام OCR مباشرة
    ocr_lang: 'eng' للإنجليزية، 'ara' للعربية، 'eng+ara' للاثنين
    """
    try:
        print("\n" + "="*60)
        print("🚀 بدء معالجة ملف PDF")
        print("="*60)
        
        texts = extract_text_from_pdf(input_path, use_ocr, ocr_lang)
        result = create_pdf(texts, output_path)
        
        print("\n" + "="*60)
        print("✅ اكتملت المعالجة بنجاح!")
        print("="*60 + "\n")
        
        return result
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ فشلت العملية: {e}")
        print("="*60 + "\n")
        raise


if __name__ == "__main__":
    print("\n🔧 معالج PDF مع دعم OCR\n")
    
    # إعدادات الملف
    input_file = "upload_20251203_025931.pdf"
    output_file = "arabic_output_ocr.pdf"
    
    # اختر اللغة:
    # 'eng' = إنجليزي فقط
    # 'ara' = عربي فقط  
    # 'eng+ara' = إنجليزي وعربي
    
    try:
        # المحاولة الأولى: بدون OCR (أسرع)
        print("🔄 محاولة الاستخراج العادي أولاً...\n")
        process_pdf_file(input_file, output_file, use_ocr=False)
        
    except Exception as e:
        print("\n" + "="*60)
        print("💡 الطرق العادية فشلت. هل تريد استخدام OCR؟")
        print("="*60)
        print("\nلاستخدام OCR:")
        print("1. ثبت المكتبات:")
        print("   pip install pdf2image pytesseract pillow")
        print("\n2. حمّل Tesseract OCR من:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print("\n3. حدّث مسار TESSERACT_PATH في الكود")
        print("\n4. شغّل الكود مرة أخرى مع use_ocr=True")
        print(f"\n   process_pdf_file('{input_file}', '{output_file}', use_ocr=True, ocr_lang='eng')")
        print("\n" + "="*60)

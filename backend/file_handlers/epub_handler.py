"""
معالج ملفات EPUB (الكتب الإلكترونية)
يستخرج النص ويعيد إنشاء EPUB بالعربي مع دعم RTL كامل
مثالي لترجمة الروايات الكاملة بدون حد
"""

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


def extract_text_from_epub(file_path):
    """
    استخراج النص من ملف EPUB
    
    Args:
        file_path (str): مسار الملف
        
    Returns:
        list: قائمة النصوص (كل فصل = عنصر)
    """
    try:
        book = epub.read_epub(file_path)
        texts = []
        
        # المرور على كل عنصر في الكتاب
        for item in book.get_items():
            # نبحث عن المحتوى النصي (HTML)
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # تحويل HTML لنص
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                
                # استخراج النص وتنظيفه
                text = soup.get_text(separator='\n', strip=True)
                
                if text.strip():
                    texts.append(text.strip())
        
        if not texts:
            raise Exception("الملف فارغ أو لا يحتوي على نص قابل للقراءة")
        
        return texts
    
    except Exception as e:
        raise Exception(f"خطأ في قراءة ملف EPUB: {str(e)}")


def create_epub(texts, output_path, title="كتاب مترجم", author="الآنسة فصيحة"):
    """
    إنشاء ملف EPUB من نصوص عربية مترجمة مع دعم RTL
    
    Args:
        texts (list): قائمة النصوص المترجمة
        output_path (str): مسار الملف الناتج
        title (str): عنوان الكتاب
        author (str): المؤلف
        
    Returns:
        str: مسار الملف المحفوظ
    """
    try:
        # إنشاء كتاب جديد
        book = epub.EpubBook()
        
        # Metadata
        book.set_identifier('id_translated_book')
        book.set_title(title)
        book.set_language('ar')
        book.add_author(author)
        
        # ✅ CSS للعربية مع RTL
        arabic_css = '''
        @page {
            margin: 2cm;
        }
        body {
            font-family: 'Traditional Arabic', 'Amiri', 'Arial', sans-serif;
            direction: rtl;
            text-align: right;
            line-height: 1.8;
            font-size: 1.1em;
        }
        p {
            text-align: right;
            margin: 1em 0;
            text-indent: 2em;
        }
        h1, h2, h3 {
            text-align: right;
            direction: rtl;
        }
        '''
        
        # إضافة CSS
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=arabic_css
        )
        book.add_item(nav_css)
        
        # إنشاء الفصول
        chapters = []
        spine = ['nav']
        
        for i, text in enumerate(texts, 1):
            # إنشاء فصل
            chapter = epub.EpubHtml(
                title=f'الفصل {i}',
                file_name=f'chap_{i:03d}.xhtml',
                lang='ar'
            )
            
            # تقسيم النص لفقرات
            paragraphs = text.split('\n')
            paragraphs_html = ''.join([f'<p>{p.strip()}</p>' for p in paragraphs if p.strip()])
            
            # ✅ محتوى HTML مع RTL
            chapter.content = f'''
            <html dir="rtl" lang="ar">
            <head>
                <link rel="stylesheet" href="../style/nav.css" type="text/css"/>
            </head>
            <body>
                <h1>الفصل {i}</h1>
                {paragraphs_html}
            </body>
            </html>
            '''
            
            book.add_item(chapter)
            chapters.append(chapter)
            spine.append(chapter)
        
        # Table of Contents
        book.toc = tuple(chapters)
        
        # إضافة Navigation files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Spine (ترتيب القراءة)
        book.spine = spine
        
        # حفظ الملف
        epub.write_epub(output_path, book, {})
        
        return output_path
    
    except Exception as e:
        raise Exception(f"خطأ في إنشاء ملف EPUB: {str(e)}")


# اختبار
if __name__ == "__main__":
    print("✅ EPUB Handler جاهز!")
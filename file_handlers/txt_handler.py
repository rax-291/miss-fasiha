"""
معالج ملفات TXT
يستخرج النص من ملفات نصية عادية ويعيد إنشائها
"""

def extract_text_from_txt(file_path):
    """
    استخراج النص من ملف TXT
    
    Args:
        file_path (str): مسار الملف
        
    Returns:
        list: قائمة تحتوي على النص (كل الملف كعنصر واحد)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # نرجع النص كقائمة (للتوحيد مع باقي المعالجات)
        return [content] if content.strip() else []
    
    except UnicodeDecodeError:
        # في حال الترميز مش UTF-8، نجرب ترميزات أخرى
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            return [content] if content.strip() else []
        except Exception as e:
            raise Exception(f"خطأ في قراءة الملف: {str(e)}")
    
    except Exception as e:
        raise Exception(f"خطأ في قراءة ملف TXT: {str(e)}")


def create_txt(texts, output_path):
    """
    إنشاء ملف TXT من نصوص مترجمة
    
    Args:
        texts (list): قائمة النصوص المترجمة
        output_path (str): مسار الملف الناتج
        
    Returns:
        str: مسار الملف المحفوظ
    """
    try:
        # دمج كل النصوص
        full_text = '\n\n'.join(texts)
        
        # حفظ الملف بترميز UTF-8 (يدعم العربي)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        return output_path
    
    except Exception as e:
        raise Exception(f"خطأ في إنشاء ملف TXT: {str(e)}")


# اختبار
if __name__ == "__main__":
    print("✅ TXT Handler جاهز!")
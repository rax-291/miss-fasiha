/* ============================ */
/* عناصر DOM الأساسية          */
/* ============================ */
const bodyEl = document.body;
const navLinks = document.querySelectorAll('.main-nav a');

const src = document.getElementById('source-text');
const dst = document.getElementById('translated-text');
const sourceLabel = document.getElementById('source-label');
const targetLabel = document.getElementById('target-label');
const swapBtn = document.getElementById('swap-langs');

const translateBtn = document.getElementById('translate-btn');
const copyBtn = document.getElementById('copy-btn');
const downloadBtn = document.getElementById('download-btn');
const clearBtn = document.getElementById('clear-btn');
const speakBtn = document.getElementById('speak-btn');
// منع تعديل النص المترجم يدويًا
dst.addEventListener('input', (e) => {
  if (!dst.readOnly) return;
  e.preventDefault();
  dst.value = dst.value; // يرجع النص كما هو
});

// نرجع زر الحذف يشتغل
clearBtn?.addEventListener('click', ()=>{ dst.value = ''; });



/* ============================ */
/* تنقل لطيف + تثبيت عرض الأقسام */
/* ============================ */
function setFocusModeFromHash(){
  if (location.hash === '#translate-section'){
    bodyEl.classList.add('focus-translate'); // ممكن تستعمليها لاحقًا
  } else {
    bodyEl.classList.remove('focus-translate');
  }
}
setFocusModeFromHash();
window.addEventListener('hashchange', setFocusModeFromHash);

/* سكرول ناعم + تعويض ارتفاع الشريط */
navLinks.forEach(a=>{
  a.addEventListener('click', (e)=>{
    const id = a.getAttribute('href');
    if(!id || !id.startsWith('#')) return;
    e.preventDefault();
    history.pushState(null, '', id);
    setFocusModeFromHash();
    const target = document.querySelector(id);
    if(target){
      const navH = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-h')) || 56;
      const y = target.getBoundingClientRect().top + window.scrollY - navH - 10;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  });
});

/* ============================ */
/* اللغة الافتراضية: EN → AR   */
/* ============================ */
let currentSourceLang = 'en';
let currentTargetLang = 'ar';

function applyLangUI(){
  sourceLabel.textContent = currentSourceLang === 'ar' ? 'العربية' : 'الإنجليزية';
  targetLabel.textContent = currentTargetLang === 'ar' ? 'العربية' : 'الإنجليزية';
  src.setAttribute('dir', currentSourceLang === 'ar' ? 'rtl':'ltr');
  dst.setAttribute('dir', currentTargetLang === 'ar' ? 'rtl':'ltr');
  src.placeholder = currentSourceLang === 'ar' ? 'اكتب أو الصق النص هنا...' : 'Type or paste text here...';
  dst.placeholder = currentTargetLang === 'ar' ? 'ستظهر الترجمة هنا...' : 'Translation will appear here...';
}
applyLangUI();

swapBtn?.addEventListener('click', ()=>{
  [currentSourceLang, currentTargetLang] = [currentTargetLang, currentSourceLang];
  applyLangUI();  // يبدل اللغات فقط
});

/* ============================ */
/* الترجمة (Placeholder)        */
/* ============================ */
translateBtn?.addEventListener('click', async ()=>{
  const text = src.value.trim();
  const file = window.uploadedFile; // الملف المرفوع (إن وجد)
  
  // حالة 1: ترجمة ملف
  if (file) {
    dst.value = '⏳ جاري ترجمة الملف... قد يستغرق عدة دقائق حسب حجم الملف';
    translateBtn.disabled = true;
    downloadBtn.disabled = true;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('use_two_stage', 'true');
    
    try {
      const response = await fetch('http://localhost:5000/api/translate-file', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'فشلت الترجمة');
      }
      
      // حفظ الملف المترجم
      const blob = await response.blob();
      const originalName = file.name;
      const ext = originalName.split('.').pop();
      const baseName = originalName.replace(/\.[^/.]+$/, '');
      const translatedName = `${baseName}_translated.${ext}`;
      
      // حفظ للتنزيل
      window.translatedFileBlob = blob;
      window.translatedFileName = translatedName;
      
      dst.value = `✅ تمت ترجمة الملف بنجاح!\n\n📥 اضغط زر التنزيل للحصول على الملف المترجم\n\n📄 اسم الملف: ${translatedName}`;
      downloadBtn.disabled = false;
      
    } catch(error) {
      console.error('خطأ في ترجمة الملف:', error);
      dst.value = `❌ حدث خطأ في ترجمة الملف\n\n${error.message}\n\n💡 تأكد من:\n- تشغيل Backend (python app.py)\n- اتصال الإنترنت\n- حجم الملف مناسب`;
    } finally {
      translateBtn.disabled = false;
    }
  }
  // حالة 2: ترجمة نص مباشر
  else if (text) {
    dst.value = '⏳ جاري الترجمة...';
    translateBtn.disabled = true;
    
    try {
      const response = await fetch('http://localhost:5000/api/translate-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: text,
          use_two_stage: true
        })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'فشلت الترجمة');
      }
      
      const data = await response.json();
      dst.value = data.translation;
      
    } catch(error) {
      console.error('خطأ في الترجمة:', error);
      dst.value = `❌ حدث خطأ في الترجمة\n\n${error.message}\n\n💡 تأكد من تشغيل Backend:\nفي Terminal اكتب: python app.py`;
    } finally {
      translateBtn.disabled = false;
    }
  }
  // حالة 3: لا يوجد نص ولا ملف
  else {
    dst.value = '';
  }
});


/* نسخ / مسح / استماع */
copyBtn?.addEventListener('click', ()=>{ if(dst.value) navigator.clipboard.writeText(dst.value); });
clearBtn?.addEventListener('click', ()=>{ dst.value = ''; });

speakBtn?.addEventListener('click', ()=>{
  const text = dst.value || src.value;
  if(!text) return;
  const u = new SpeechSynthesisUtterance(text);
  u.lang = currentTargetLang === 'ar' ? 'ar' : 'en-US';
  speechSynthesis.speak(u);
});

/* ============================ */
/* الشات بوت (مودال + تفاعل)   */
/* ============================ */
document.addEventListener('DOMContentLoaded', () => {
  const chatModal = document.getElementById('chatbot-modal');
  const chatBody = document.getElementById('chat-body');
  const chatInput = document.getElementById('chat-input');
  const sendChatBtn = document.getElementById('send-chat-btn');
  const openChatBtn = document.getElementById('open-chat-inline');
  const closeChatBtn = document.getElementById('close-chat');
const API_URL= 'http://127.0.0.1:8000/api/chat';
  
  function appendMessage(msg, sender='bot') {
    const div = document.createElement('div');
    div.className = `msg ${sender}`;
    div.textContent = msg;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function sendMessage() {
    const msg = chatInput.value.trim();
    if(!msg) return;
    appendMessage(msg, 'user');
    chatInput.value = '';


    fetch("http://127.0.0.1:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg }),
    })
    .then(faq=>  faq.json())
    .then(data => appendMessage(data.reply, 'bot'))
    .catch(err => {
      appendMessage('❌ خطأ في الاتصال بالباك اند', 'bot');
      console.error(err);
    });
  }

  // فتح المودال
  openChatBtn?.addEventListener('click', ()=>{
    chatModal.style.display = 'block';
    chatModal.setAttribute('aria-hidden', 'false');
    chatInput.focus();
  });

  // إغلاق المودال
  closeChatBtn?.addEventListener('click', ()=>{
    chatModal.style.display = 'none';
    chatModal.setAttribute('aria-hidden', 'true');
  });

  // زر إرسال
  sendChatBtn?.addEventListener('click', sendMessage);
  chatInput?.addEventListener('keydown', (e)=>{
    if(e.key === 'Enter' && !e.shiftKey){
      e.preventDefault();
      sendMessage();
    }
  });
});
const chatFloatBtn = document.getElementById('chat-float-btn');
const chatModal = document.getElementById('chatbot-modal');
const closeChatBtn = document.getElementById('close-chat');

chatFloatBtn.addEventListener('click', () => {
  // فتح المودال الحالي
  chatModal.style.display = 'block';
  chatModal.setAttribute('aria-hidden', 'false');
});

closeChatBtn.addEventListener('click', () => {
  // إغلاق المودال
  chatModal.style.display = 'none';
  chatModal.setAttribute('aria-hidden', 'true');
});

// إغلاق عند الضغط خارج المودال
window.addEventListener('click', (e) => {
  if (e.target === chatModal) {
    chatModal.style.display = 'none';
    chatModal.setAttribute('aria-hidden', 'true');
  }
});


/* ============================ */
/* رفع الملفات + التنزيل بنفس الصيغة */
/* ============================ */
const fileInput = document.getElementById('upload-file');

fileInput?.addEventListener('change', function() {
  const file = fileInput.files[0];
  if (!file) return;

  const allowedExts = ['pdf', 'txt', 'doc', 'docx', 'epub'];
  const ext = file.name.split('.').pop().toLowerCase();
  
  if (!allowedExts.includes(ext)) {
    alert("⚠️ نوع الملف غير مدعوم!\n\nالمدعوم: PDF, DOCX, TXT, EPUB");
    fileInput.value = "";
    return;
  }
  
  // حساب حجم الملف
  const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
  
  // حفظ الملف للاستخدام عند الترجمة
  window.uploadedFile = file;
  
  // مسح الملف المترجم السابق
  window.translatedFileBlob = null;
  window.translatedFileName = null;
  
  src.value = `✅ تم رفع الملف بنجاح!\n\n📄 الاسم: ${file.name}\n📊 الحجم: ${sizeMB} MB\n📝 النوع: ${ext.toUpperCase()}\n\n⬇️ اضغط "ترجمة الآن" لبدء الترجمة`;
  dst.value = 'ستظهر نتيجة الترجمة هنا...';
  
  // تنبيه للملفات الكبيرة
  if (file.size > 5 * 1024 * 1024) { // أكبر من 5 MB
    alert(`📚 ملف كبير (${sizeMB} MB)\n\n⏰ قد تستغرق الترجمة عدة دقائق\nالرجاء الانتظار بعد الضغط على "ترجمة الآن"`);
  }
});

downloadBtn?.addEventListener('click', async () => {
  try {
    // حالة 1: تنزيل ملف مترجم من Backend
    if (window.translatedFileBlob && window.translatedFileName) {
      const url = URL.createObjectURL(window.translatedFileBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = window.translatedFileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      alert('✅ تم تنزيل الملف المترجم!');
      return;
    } 

    // الامتداد الافتراضي
    let ext = 'txt';
    let base = 'translation';

    const original = window.uploadedFile;
    const payload = dst.value.trim();

    if (original) {
      const name = original.name;
      base = name.replace(/\.[^/.]+$/, '');
      if (/\.pdf$/i.test(name)) ext = 'pdf';
      else if (/\.(docx|doc)$/i.test(name)) ext = 'docx'; // نحفظ doc كـ docx
      else if (/\.txt$/i.test(name)) ext = 'txt';
    }

    const filename = `${base}_translated.${ext}`;

    if (ext === 'txt') {
      if (!payload || payload.includes('❌') || payload.includes('⏳')) {
        alert('⚠️ لا يوجد ترجمة جاهزة للتنزيل');
        return;
      }
      const blob = new Blob([payload], { type: 'text/plain;charset=utf-8' });
      triggerDownload(blob, filename);
      alert('✅ تم حفظ الترجمة كملف نصي!');
    } else if (ext === 'docx') {
      // ===== DOCX باستخدام docx =====
      const { Document, Packer, Paragraph, TextRun } = window.docx || {};
      if (!Document) throw new Error('docx library not loaded');
      const paras = payload.split(/\r?\n/).map(line =>
        new Paragraph({ children: [ new TextRun({ text: line }) ] })
      );
      const doc = new Document({
        sections: [{ properties: {}, children: paras }]
      });
      const blob = await Packer.toBlob(doc);
      triggerDownload(blob, filename);
    } else if (ext === 'pdf') {
      // ===== PDF باستخدام jsPDF =====
      const { jsPDF } = window.jspdf || {};
      if (!jsPDF) throw new Error('jsPDF library not loaded');

      const doc = new jsPDF({ unit: 'pt', format: 'a4' });
      const margin = 40;
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const maxWidth = pageWidth - margin * 2;
      const lineHeight = 18;

      let y = margin;
      const lines = doc.splitTextToSize(payload, maxWidth);

      lines.forEach((ln) => {
        if (y + lineHeight > pageHeight - margin) {
          doc.addPage();
          y = margin;
        }
        doc.text(String(ln), margin, y, { align: 'left' });
        y += lineHeight;
      });

      const blob = doc.output('blob');
      triggerDownload(blob, filename);
    }
  } catch (error) {
    console.error('خطأ في تجهيز التنزيل:', error);
    alert(`❌ حدث خطأ أثناء التحضير للتنزيل\n\n${error.message}`);
  }
});


// أداة تنزيل موحدة
function triggerDownload(blob, name) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 500);
}

// الضغط على Enter يبدأ الترجمة
src?.addEventListener('keydown', (e)=>{
  if(e.key === 'Enter' && !e.shiftKey){
    e.preventDefault();
    translateBtn.click();
  }
});


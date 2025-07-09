#!/bin/bash

# Ben Odinsight - Limitless Template Integration Script
# GitHub repo klasörünüzün yolunu değiştirin
LIMITLESS_PATH="/opt/odinsight/bs5"
PROJECT_PATH="/opt/odinsight"

echo "🚀 Limitless template dosyaları kopyalanıyor..."

cd $PROJECT_PATH

# CSS dosyalarını kopyala
echo "📁 CSS dosyaları kopyalanıyor..."
mkdir -p static/vendor/limitless/css/ltr
mkdir -p static/vendor/limitless/css/rtl

cp $LIMITLESS_PATH/html/layout_1/full/assets/css/ltr/*.css static/vendor/limitless/css/ltr/
cp $LIMITLESS_PATH/html/layout_1/full/assets/css/rtl/*.css static/vendor/limitless/css/rtl/

# JavaScript dosyalarını kopyala
echo "📁 JavaScript dosyaları kopyalanıyor..."
mkdir -p static/vendor/js/jquery
mkdir -p static/vendor/js/bootstrap

cp $LIMITLESS_PATH/assets/js/jquery/jquery.min.js static/vendor/js/jquery/
cp $LIMITLESS_PATH/assets/js/bootstrap/bootstrap.bundle.min.js static/vendor/js/bootstrap/

# Vendor JS dosyalarını kopyala
echo "📁 Vendor JavaScript dosyaları kopyalanıyor..."
cp -r $LIMITLESS_PATH/assets/js/vendor/* static/vendor/js/vendor/

# Icon'ları kopyala
echo "📁 Icon dosyaları kopyalanıyor..."
mkdir -p static/vendor/icons
cp -r $LIMITLESS_PATH/assets/icons/* static/vendor/icons/

# Font'ları kopyala
echo "📁 Font dosyaları kopyalanıyor..."
mkdir -p static/vendor/fonts
cp -r $LIMITLESS_PATH/assets/fonts/* static/vendor/fonts/

# Demo resimlerini kopyala
echo "📁 Demo resimleri kopyalanıyor..."
mkdir -p static/images/demo
cp -r $LIMITLESS_PATH/assets/images/demo/* static/images/demo/

# Ana app.js dosyasını kopyala
echo "📁 Ana JavaScript dosyası kopyalanıyor..."
cp $LIMITLESS_PATH/html/layout_1/full/assets/js/app.js static/js/limitless-app.js

# Demo JavaScript dosyalarını kopyala (dashboard için)
echo "📁 Demo JavaScript dosyaları kopyalanıyor..."
mkdir -p static/js/demo
cp -r $LIMITLESS_PATH/assets/demo/* static/js/demo/

# Placeholder resim oluştur
echo "📁 Placeholder resim oluşturuluyor..."
mkdir -p static/images
echo '<svg width="38" height="38" xmlns="http://www.w3.org/2000/svg"><rect width="38" height="38" fill="#ccc"/><text x="19" y="19" text-anchor="middle" dy=".3em" fill="#999">User</text></svg>' > static/images/placeholder.svg

# Dosya izinlerini ayarla
echo "🔧 Dosya izinleri ayarlanıyor..."
chmod -R 755 static/

echo "✅ Limitless template dosyaları başarıyla kopyalandı!"
echo ""
echo "🎯 Sıradaki adımlar:"
echo "1. docker-compose restart web"
echo "2. python manage.py collectstatic"
echo "3. http://localhost:8000 adresini test edin"
echo ""
echo "📂 Kopyalanan dosyalar:"
echo "   - CSS: static/vendor/limitless/css/"
echo "   - JS: static/vendor/js/ ve static/js/limitless-app.js"
echo "   - Icons: static/vendor/icons/"
echo "   - Fonts: static/vendor/fonts/"
echo "   - Images: static/images/demo/"

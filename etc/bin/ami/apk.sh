ANDROID_NDK_ROOT=/home/ubuntu/android-ndk-r12b
QT_ROOT=/home/ubuntu/Qt
$QT_ROOT/5.7/android_armv7/bin/qmake /home/ubuntu/scewpt/qml/latestgreatest.pro -r -spec android-g++
$ANDROID_NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++ -c -Wno-psabi -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums -DANDROID -Wa,--noexecstack -fno-builtin-memmove -std=c++11 -O2 -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -mthumb -Wall -Wno-psabi -W -D_REENTRANT -fPIC -DQT_NO_DEBUG -DQT_QUICK_LIB -DQT_SVG_LIB -DQT_WIDGETS_LIB -DQT_GUI_LIB -DQT_QML_LIB -DQT_NETWORK_LIB -DQT_CORE_LIB -I/home/ubuntu/scewpt/qml -I. -I$QT_ROOT/5.7/android_armv7/include -I$QT_ROOT/5.7/android_armv7/include/QtQuick -I$QT_ROOT/5.7/android_armv7/include/QtSvg -I$QT_ROOT/5.7/android_armv7/include/QtWidgets -I$QT_ROOT/5.7/android_armv7/include/QtGui -I$QT_ROOT/5.7/android_armv7/include/QtQml -I$QT_ROOT/5.7/android_armv7/include/QtNetwork -I$QT_ROOT/5.7/android_armv7/include/QtCore -I. -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/include -isystem $ANDROID_NDK_ROOT/platforms/android-9/arch-arm/usr/include -I$QT_ROOT/5.7/android_armv7/mkspecs/android-g++ -o main.o /home/ubuntu/scewpt/qml/main.cpp

$QT_ROOT/5.7/android_armv7/bin/rcc -name index /home/ubuntu/scewpt/qml/index.qrc -o qrc_index.cpp
$ANDROID_NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++ -c -Wno-psabi -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums -DANDROID -Wa,--noexecstack -fno-builtin-memmove -std=c++11 -O2 -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -mthumb -Wall -Wno-psabi -W -D_REENTRANT -fPIC -DQT_NO_DEBUG -DQT_QUICK_LIB -DQT_SVG_LIB -DQT_WIDGETS_LIB -DQT_GUI_LIB -DQT_QML_LIB -DQT_NETWORK_LIB -DQT_CORE_LIB -I/home/ubuntu/scewpt/qml -I. -I$QT_ROOT/5.7/android_armv7/include -I$QT_ROOT/5.7/android_armv7/include/QtQuick -I$QT_ROOT/5.7/android_armv7/include/QtSvg -I$QT_ROOT/5.7/android_armv7/include/QtWidgets -I$QT_ROOT/5.7/android_armv7/include/QtGui -I$QT_ROOT/5.7/android_armv7/include/QtQml -I$QT_ROOT/5.7/android_armv7/include/QtNetwork -I$QT_ROOT/5.7/android_armv7/include/QtCore -I. -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/include -isystem $ANDROID_NDK_ROOT/platforms/android-9/arch-arm/usr/include -I$QT_ROOT/5.7/android_armv7/mkspecs/android-g++ -o qrc_index.o qrc_index.cpp
$QT_ROOT/5.7/android_armv7/bin/rcc -name info /home/ubuntu/scewpt/qml/info.qrc -o qrc_info.cpp
$ANDROID_NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++ -c -Wno-psabi -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums -DANDROID -Wa,--noexecstack -fno-builtin-memmove -std=c++11 -O2 -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -mthumb -Wall -Wno-psabi -W -D_REENTRANT -fPIC -DQT_NO_DEBUG -DQT_QUICK_LIB -DQT_SVG_LIB -DQT_WIDGETS_LIB -DQT_GUI_LIB -DQT_QML_LIB -DQT_NETWORK_LIB -DQT_CORE_LIB -I/home/ubuntu/scewpt/qml -I. -I$QT_ROOT/5.7/android_armv7/include -I$QT_ROOT/5.7/android_armv7/include/QtQuick -I$QT_ROOT/5.7/android_armv7/include/QtSvg -I$QT_ROOT/5.7/android_armv7/include/QtWidgets -I$QT_ROOT/5.7/android_armv7/include/QtGui -I$QT_ROOT/5.7/android_armv7/include/QtQml -I$QT_ROOT/5.7/android_armv7/include/QtNetwork -I$QT_ROOT/5.7/android_armv7/include/QtCore -I. -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/include -isystem $ANDROID_NDK_ROOT/platforms/android-9/arch-arm/usr/include -I$QT_ROOT/5.7/android_armv7/mkspecs/android-g++ -o qrc_info.o qrc_info.cpp
$QT_ROOT/5.7/android_armv7/bin/rcc -name media /home/ubuntu/scewpt/qml/media.qrc -o qrc_media.cpp
$ANDROID_NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++ -c -Wno-psabi -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums -DANDROID -Wa,--noexecstack -fno-builtin-memmove -std=c++11 -O2 -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -mthumb -Wall -Wno-psabi -W -D_REENTRANT -fPIC -DQT_NO_DEBUG -DQT_QUICK_LIB -DQT_SVG_LIB -DQT_WIDGETS_LIB -DQT_GUI_LIB -DQT_QML_LIB -DQT_NETWORK_LIB -DQT_CORE_LIB -I/home/ubuntu/scewpt/qml -I. -I$QT_ROOT/5.7/android_armv7/include -I$QT_ROOT/5.7/android_armv7/include/QtQuick -I$QT_ROOT/5.7/android_armv7/include/QtSvg -I$QT_ROOT/5.7/android_armv7/include/QtWidgets -I$QT_ROOT/5.7/android_armv7/include/QtGui -I$QT_ROOT/5.7/android_armv7/include/QtQml -I$QT_ROOT/5.7/android_armv7/include/QtNetwork -I$QT_ROOT/5.7/android_armv7/include/QtCore -I. -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/include -isystem $ANDROID_NDK_ROOT/platforms/android-9/arch-arm/usr/include -I$QT_ROOT/5.7/android_armv7/mkspecs/android-g++ -o qrc_media.o qrc_media.cpp
$QT_ROOT/5.7/android_armv7/bin/rcc -name maybe /home/ubuntu/scewpt/qml/maybe.qrc -o qrc_maybe.cpp
$ANDROID_NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++ -c -Wno-psabi -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums -DANDROID -Wa,--noexecstack -fno-builtin-memmove -std=c++11 -O2 -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -mthumb -Wall -Wno-psabi -W -D_REENTRANT -fPIC -DQT_NO_DEBUG -DQT_QUICK_LIB -DQT_SVG_LIB -DQT_WIDGETS_LIB -DQT_GUI_LIB -DQT_QML_LIB -DQT_NETWORK_LIB -DQT_CORE_LIB -I/home/ubuntu/scewpt/qml -I. -I$QT_ROOT/5.7/android_armv7/include -I$QT_ROOT/5.7/android_armv7/include/QtQuick -I$QT_ROOT/5.7/android_armv7/include/QtSvg -I$QT_ROOT/5.7/android_armv7/include/QtWidgets -I$QT_ROOT/5.7/android_armv7/include/QtGui -I$QT_ROOT/5.7/android_armv7/include/QtQml -I$QT_ROOT/5.7/android_armv7/include/QtNetwork -I$QT_ROOT/5.7/android_armv7/include/QtCore -I. -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/include -isystem $ANDROID_NDK_ROOT/platforms/android-9/arch-arm/usr/include -I$QT_ROOT/5.7/android_armv7/mkspecs/android-g++ -o qrc_maybe.o qrc_maybe.cpp
$QT_ROOT/5.7/android_armv7/bin/rcc -name scripts /home/ubuntu/scewpt/qml/scripts.qrc -o qrc_scripts.cpp
$ANDROID_NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++ -c -Wno-psabi -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums -DANDROID -Wa,--noexecstack -fno-builtin-memmove -std=c++11 -O2 -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -mthumb -Wall -Wno-psabi -W -D_REENTRANT -fPIC -DQT_NO_DEBUG -DQT_QUICK_LIB -DQT_SVG_LIB -DQT_WIDGETS_LIB -DQT_GUI_LIB -DQT_QML_LIB -DQT_NETWORK_LIB -DQT_CORE_LIB -I/home/ubuntu/scewpt/qml -I. -I$QT_ROOT/5.7/android_armv7/include -I$QT_ROOT/5.7/android_armv7/include/QtQuick -I$QT_ROOT/5.7/android_armv7/include/QtSvg -I$QT_ROOT/5.7/android_armv7/include/QtWidgets -I$QT_ROOT/5.7/android_armv7/include/QtGui -I$QT_ROOT/5.7/android_armv7/include/QtQml -I$QT_ROOT/5.7/android_armv7/include/QtNetwork -I$QT_ROOT/5.7/android_armv7/include/QtCore -I. -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/include -isystem $ANDROID_NDK_ROOT/platforms/android-9/arch-arm/usr/include -I$QT_ROOT/5.7/android_armv7/mkspecs/android-g++ -o qrc_scripts.o qrc_scripts.cpp
$QT_ROOT/5.7/android_armv7/bin/rcc -name sites /home/ubuntu/scewpt/qml/sites.qrc -o qrc_sites.cpp
$ANDROID_NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++ -c -Wno-psabi -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums -DANDROID -Wa,--noexecstack -fno-builtin-memmove -std=c++11 -O2 -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -mthumb -Wall -Wno-psabi -W -D_REENTRANT -fPIC -DQT_NO_DEBUG -DQT_QUICK_LIB -DQT_SVG_LIB -DQT_WIDGETS_LIB -DQT_GUI_LIB -DQT_QML_LIB -DQT_NETWORK_LIB -DQT_CORE_LIB -I/home/ubuntu/scewpt/qml -I. -I$QT_ROOT/5.7/android_armv7/include -I$QT_ROOT/5.7/android_armv7/include/QtQuick -I$QT_ROOT/5.7/android_armv7/include/QtSvg -I$QT_ROOT/5.7/android_armv7/include/QtWidgets -I$QT_ROOT/5.7/android_armv7/include/QtGui -I$QT_ROOT/5.7/android_armv7/include/QtQml -I$QT_ROOT/5.7/android_armv7/include/QtNetwork -I$QT_ROOT/5.7/android_armv7/include/QtCore -I. -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/include -isystem $ANDROID_NDK_ROOT/platforms/android-9/arch-arm/usr/include -I$QT_ROOT/5.7/android_armv7/mkspecs/android-g++ -o qrc_sites.o qrc_sites.cpp
$QT_ROOT/5.7/android_armv7/bin/rcc -name statusbar /home/ubuntu/scewpt/qml/statusbar.qrc -o qrc_statusbar.cpp
$ANDROID_NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++ -c -Wno-psabi -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums -DANDROID -Wa,--noexecstack -fno-builtin-memmove -std=c++11 -O2 -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -mthumb -Wall -Wno-psabi -W -D_REENTRANT -fPIC -DQT_NO_DEBUG -DQT_QUICK_LIB -DQT_SVG_LIB -DQT_WIDGETS_LIB -DQT_GUI_LIB -DQT_QML_LIB -DQT_NETWORK_LIB -DQT_CORE_LIB -I/home/ubuntu/scewpt/qml -I. -I$QT_ROOT/5.7/android_armv7/include -I$QT_ROOT/5.7/android_armv7/include/QtQuick -I$QT_ROOT/5.7/android_armv7/include/QtSvg -I$QT_ROOT/5.7/android_armv7/include/QtWidgets -I$QT_ROOT/5.7/android_armv7/include/QtGui -I$QT_ROOT/5.7/android_armv7/include/QtQml -I$QT_ROOT/5.7/android_armv7/include/QtNetwork -I$QT_ROOT/5.7/android_armv7/include/QtCore -I. -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/include -isystem $ANDROID_NDK_ROOT/platforms/android-9/arch-arm/usr/include -I$QT_ROOT/5.7/android_armv7/mkspecs/android-g++ -o qrc_statusbar.o qrc_statusbar.cpp
$QT_ROOT/5.7/android_armv7/bin/rcc -name toolbar /home/ubuntu/scewpt/qml/toolbar.qrc -o qrc_toolbar.cpp
$ANDROID_NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++ -c -Wno-psabi -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums -DANDROID -Wa,--noexecstack -fno-builtin-memmove -std=c++11 -O2 -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -mthumb -Wall -Wno-psabi -W -D_REENTRANT -fPIC -DQT_NO_DEBUG -DQT_QUICK_LIB -DQT_SVG_LIB -DQT_WIDGETS_LIB -DQT_GUI_LIB -DQT_QML_LIB -DQT_NETWORK_LIB -DQT_CORE_LIB -I/home/ubuntu/scewpt/qml -I. -I$QT_ROOT/5.7/android_armv7/include -I$QT_ROOT/5.7/android_armv7/include/QtQuick -I$QT_ROOT/5.7/android_armv7/include/QtSvg -I$QT_ROOT/5.7/android_armv7/include/QtWidgets -I$QT_ROOT/5.7/android_armv7/include/QtGui -I$QT_ROOT/5.7/android_armv7/include/QtQml -I$QT_ROOT/5.7/android_armv7/include/QtNetwork -I$QT_ROOT/5.7/android_armv7/include/QtCore -I. -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/include -isystem $ANDROID_NDK_ROOT/platforms/android-9/arch-arm/usr/include -I$QT_ROOT/5.7/android_armv7/mkspecs/android-g++ -o qrc_toolbar.o qrc_toolbar.cpp
$QT_ROOT/5.7/android_armv7/bin/rcc -name tweets /home/ubuntu/scewpt/qml/tweets.qrc -o qrc_tweets.cpp
$ANDROID_NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++ -c -Wno-psabi -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums -DANDROID -Wa,--noexecstack -fno-builtin-memmove -std=c++11 -O2 -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -mthumb -Wall -Wno-psabi -W -D_REENTRANT -fPIC -DQT_NO_DEBUG -DQT_QUICK_LIB -DQT_SVG_LIB -DQT_WIDGETS_LIB -DQT_GUI_LIB -DQT_QML_LIB -DQT_NETWORK_LIB -DQT_CORE_LIB -I/home/ubuntu/scewpt/qml -I. -I$QT_ROOT/5.7/android_armv7/include -I$QT_ROOT/5.7/android_armv7/include/QtQuick -I$QT_ROOT/5.7/android_armv7/include/QtSvg -I$QT_ROOT/5.7/android_armv7/include/QtWidgets -I$QT_ROOT/5.7/android_armv7/include/QtGui -I$QT_ROOT/5.7/android_armv7/include/QtQml -I$QT_ROOT/5.7/android_armv7/include/QtNetwork -I$QT_ROOT/5.7/android_armv7/include/QtCore -I. -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/include -isystem $ANDROID_NDK_ROOT/platforms/android-9/arch-arm/usr/include -I$QT_ROOT/5.7/android_armv7/mkspecs/android-g++ -o qrc_tweets.o qrc_tweets.cpp
$ANDROID_NDK_ROOT/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++ --sysroot=$ANDROID_NDK_ROOT/platforms/android-9/arch-arm/ -Wl,-soname,liblatestgreatest.so -Wl,-rpath=$QT_ROOT/5.7/android_armv7/lib -Wl,--no-undefined -Wl,-z,noexecstack -shared -o liblatestgreatest.so main.o qrc_index.o qrc_info.o qrc_media.o qrc_maybe.o qrc_scripts.o qrc_sites.o qrc_statusbar.o qrc_toolbar.o qrc_tweets.o   -L$ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a -L$ANDROID_NDK_ROOT/platforms/android-9/arch-arm//usr/lib -L$QT_ROOT/5.7/android_armv7/lib -lQt5Quick -L/opt/android/ndk/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a -L/opt/android/ndk/platforms/android-9/arch-arm//usr/lib -lQt5Svg -lQt5Widgets -lQt5Gui -lQt5Qml -lQt5Network -lQt5Core -lGLESv2 -lgnustl_shared -llog -lz -lm -ldl -lc -lgcc

/usr/bin/make INSTALL_ROOT=/tmp/build-latestgreatest-Android_for_armeabi_v7a_GCC_4_9_Qt_5_7_0-Release/android-build install

$QT_ROOT/5.7/android_armv7/bin/androiddeployqt --input ~/scewpt/etc/ami/deployment-settings.json --output /tmp/build-latestgreatest-Android_for_armeabi_v7a_GCC_4_9_Qt_5_7_0-Release/android-build --deployment bundled --android-platform android-23 --jdk /usr/lib/jvm/java-8-oracle --verbose --ant /usr/bin/ant
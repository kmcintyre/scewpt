#!/bin/bash
echo $1
manifest=/home/ubuntu/scewpt/qml/android/AndroidManifest.xml
echo "start $manifest"
python /home/ubuntu/scewpt/pyscewpt/util/manifest_sub.py $2

rm -rf /tmp/latest_greatest
mkdir /tmp/latest_greatest
cd /tmp/latest_greatest
ANDROID_NDK_ROOT=/home/ubuntu/android-ndk-r14b
export ANDROID_NDK_ROOT
ANDROID_CHAIN=/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++
QT_ROOT=/home/ubuntu/Qt5.9.0

echo "variables: $PACKAGE $1 $ANDROID_NDK_ROOT $ANDROID_CHAIN $QT_ROOT"

/home/ubuntu/Qt5.9.0/5.9/android_armv7/bin/qmake -install qinstall program libplanets-qml.so 
/home/ubuntu/Qt5.9.0/Examples/Qt-5.9/qt3d/build-planets-qml-Android_for_armeabi_v7a_GCC_4_9_Qt_5_9_0_for_Android_armv7-Debug/android-build/libs/armeabi-v7a/libplanets-qml.so

$QT_ROOT/5.9/android_armv7/bin/qmake /home/ubuntu/scewpt/qml/latestgreatest.pro -r -spec android-g++ "PACKAGE=$PACKAGE"
$ANDROID_NDK_ROOT$ANDROID_CHAIN -c -Wno-psabi -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums -DANDROID -Wa,--noexecstack -fno-builtin-memmove -std=c++11 -O2 -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -mthumb -Wall -Wno-psabi -W -D_REENTRANT -fPIC -DQT_NO_DEBUG -DQT_QUICK_LIB -DQT_SVG_LIB -DQT_WIDGETS_LIB -DQT_GUI_LIB -DQT_QML_LIB -DQT_NETWORK_LIB -DQT_CORE_LIB -I/home/ubuntu/scewpt/qml -I. -I$QT_ROOT/5.7/android_armv7/include -I$QT_ROOT/5.7/android_armv7/include/QtQuick -I$QT_ROOT/5.7/android_armv7/include/QtSvg -I$QT_ROOT/5.7/android_armv7/include/QtWidgets -I$QT_ROOT/5.7/android_armv7/include/QtGui -I$QT_ROOT/5.7/android_armv7/include/QtQml -I$QT_ROOT/5.7/android_armv7/include/QtNetwork -I$QT_ROOT/5.7/android_armv7/include/QtCore -I. -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/include -isystem $ANDROID_NDK_ROOT/platforms/android-9/arch-arm/usr/include -I$QT_ROOT/5.7/android_armv7/mkspecs/android-g++ -o main.o /home/ubuntu/scewpt/qml/main.cpp

echo "main done"

pages=( index media maybe scripts sites statusbar toolbar tweets )
for i in "${pages[@]}"
do
	echo "page: $i"
	$QT_ROOT/5.9/android_armv7/bin/rcc -name $i /home/ubuntu/scewpt/qml/$i.qrc -o qrc_$i.cpp
	$ANDROID_NDK_ROOT$ANDROID_CHAIN -c -Wno-psabi -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums -DANDROID -Wa,--noexecstack -fno-builtin-memmove -std=c++11 -O2 -Os -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 -mthumb -Wall -Wno-psabi -W -D_REENTRANT -fPIC -DQT_NO_DEBUG -DQT_QUICK_LIB -DQT_SVG_LIB -DQT_WIDGETS_LIB -DQT_GUI_LIB -DQT_QML_LIB -DQT_NETWORK_LIB -DQT_CORE_LIB -I/home/ubuntu/scewpt/qml -I. -I$QT_ROOT/5.7/android_armv7/include -I$QT_ROOT/5.7/android_armv7/include/QtQuick -I$QT_ROOT/5.7/android_armv7/include/QtSvg -I$QT_ROOT/5.7/android_armv7/include/QtWidgets -I$QT_ROOT/5.7/android_armv7/include/QtGui -I$QT_ROOT/5.7/android_armv7/include/QtQml -I$QT_ROOT/5.7/android_armv7/include/QtNetwork -I$QT_ROOT/5.7/android_armv7/include/QtCore -I. -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/include -isystem $ANDROID_NDK_ROOT/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/include -isystem $ANDROID_NDK_ROOT/platforms/android-9/arch-arm/usr/include -I$QT_ROOT/5.7/android_armv7/mkspecs/android-g++ -o qrc_$i.o qrc_$i.cpp
done

/usr/bin/make INSTALL_ROOT=/tmp/latest_greatest_apk install
$QT_ROOT/5.7/android_armv7/bin/androiddeployqt --input /home/ubuntu/scewpt/etc/bin/apk/deployment-settings.json --output /tmp/latest_greatest_apk --release --deployment bundled --android-platform android-24 --jdk /usr/lib/jvm/java-8-oracle --ant /usr/bin/ant
cp /tmp/latest_greatest_apk/bin/QtApp-release-unsigned.apk $1
echo 'done'
﻿# Turn off old selected section
; 26 06 2015: Fadiga Ibrahima

; -------------------------------
; Start

  !define MUI_PRODUCT "GStock"
  !define MUI_FILE "bmain"
  !define MUI_VERSION "8.5"
  !define MUI_BRANDINGTEXT "${MUI_PRODUCT} ${MUI_VERSION}"
  !define IMAGES "images"
  !define CIMAGES "cimages"
  !define MEDIA "static"
  !define TEMPLATES "templates"
  !define CIMAGES_PATH "C:\Users\fadiga\Documents\GitHub\Common\${CIMAGES}"
  ;CRCCheck On

  !include "${NSISDIR}\Contrib\Modern UI\System.nsh"


;---------------------------------
;General

  OutFile "Install-${MUI_PRODUCT}-${MUI_VERSION}.exe"
  ShowInstDetails "nevershow"
  ShowUninstDetails "nevershow"
  ;SetCompressor off

  !define MUI_ICON "logo.ico"
  !define MUI_UNICON "logo.ico"
  !define MUI_SPECIALBITMAP "Bitmap.bmp"

;--------------------------------
;Folder selection page

  InstallDir "C:\${MUI_PRODUCT}"


;--------------------------------
;Data

  ;LicenseData "README.txt"


;--------------------------------
;Installer Sections
;Section "install" Installation info
Section "install"

;Add files
  SetOutPath "$INSTDIR"

  ;File "${MUI_FILE}.exe"
  ;File "README.txt"

  ; List of files/folders to copy
  File /r dist\*.*
  File ressources\*.dll
  ;File /r *.manifest
  ;File /r fact_source.pdf
  File /r ${IMAGES}
  File /r ${CIMAGES_PATH}
  File /r ${TEMPLATES}

;create desktop shortcut
  CreateShortCut "$DESKTOP\${MUI_PRODUCT}.lnk" "$INSTDIR\${MUI_FILE}.exe" parameters "$INSTDIR\${MEDIA}\${IMAGES}\${MUI_ICON}"

;create start-menu items
  CreateDirectory "$SMPROGRAMS\${MUI_PRODUCT}"
  CreateShortCut "$SMPROGRAMS\${MUI_PRODUCT}\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\${MEDIA}\${IMAGES}\${MUI_ICON}" 0
  CreateShortCut "$SMPROGRAMS\${MUI_PRODUCT}\${MUI_PRODUCT}.lnk" "$INSTDIR\${MUI_FILE}.exe" "" "$INSTDIR\${MEDIA}\${IMAGES}\${MUI_ICON}" 0

;write uninstall information to the registry
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${MUI_PRODUCT}" "DisplayName" "${MUI_PRODUCT} (remove only)"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${MUI_PRODUCT}" "UninstallString" "$INSTDIR\Uninstall.exe"

  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd


;--------------------------------
;Uninstaller Section
Section "Uninstall"

;Delete Files
;  RMDir /r "$INSTDIR\*.*"

;Remove the installation directory
;  RMDir "$INSTDIR"

# now delete installed file
delete $INSTDIR\*.exe
delete $INSTDIR\*.dll
;delete $INSTDIR\*.manifest
delete $INSTDIR\*.lib
delete $INSTDIR\*.zip
delete $INSTDIR\*.pdf
delete $INSTDIR\*.pyd
delete $INSTDIR\*.xlsx

RMDir /r $INSTDIR\build
RMDir /r $INSTDIR\${MEDIA}
RMDir /r $INSTDIR\${CIMAGES}
RMDir /r $INSTDIR\dist
RMDir /r $INSTDIR\tcl
RMDir /r $INSTDIR\${TEMPLATES}

;Delete Start Menu Shortcuts
  Delete "$DESKTOP\${MUI_PRODUCT}.lnk"
  Delete "$SMPROGRAMS\${MUI_PRODUCT}\*.*"
  RmDir  "$SMPROGRAMS\${MUI_PRODUCT}"

;Delete Uninstaller And Unistall Registry Entries
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\${MUI_PRODUCT}"
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${MUI_PRODUCT}"

SectionEnd

;--------------------------------
Function .onInstSuccess
  ;MessageBox MB_OK "Vous avez installé le ${MUI_PRODUCT}.Utilise son icon sur le ;bureau pour lancer le program."

   SetOutPath $INSTDIR
   ExecShell "" '"$INSTDIR\${MUI_FILE}.exe"'
FunctionEnd

Function un.onUninstSuccess
  MessageBox MB_OK "You have successfully uninstalled ${MUI_PRODUCT}."
FunctionEnd

;eof
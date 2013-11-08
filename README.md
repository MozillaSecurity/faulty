Faulty
======


###Build Instructions
---


```
% hdiutil create -volname 'FirefoxOS' -type SPARSE -fs 'Case-sensitive Journaled HFS+' -size 40g FirefoxOS.sparseimage
% open FirefoxOS.sparseimage
% cd /Volumes/FirefoxOS
```

```
% git clone https://github.com/posidron/mozilla-central
% git clone -b faulty https://github.com/posidron/B2G
% cd B2G
```

#####B2G/.userconfig
---

```
export B2G_FAULTY=1
export B2G_DEBUG=0
export B2G_NOOPT=0
export NOFTU=1
export DEVICE_DEBUG=1
export CC=/usr/local/bin/gcc-mp-4.6
export CXX=/usr/local/bin/g++-mp-4.6
export B2G_DIR=$(cd "$(dirname '$0')"; pwd -P)
# ----------------------------
# DO NOT EDIT BELOW THIS BLOCK
# ----------------------------
if [ "${USE_DISTCC}" == "1" ]; then
    export CC="distcc ${CC}"
    export CXX="distcc ${CXX}"
fi
if [ "${GECKO}" == "" ]; then
    GECKO=gecko
fi
export GECKO_PATH=${B2G_DIR}/${GECKO}
export GECKO_OBJDIR=${B2G_DIR}/objdir-gecko
if [ "${B2G_NOOPT}" == "0" ]; then
    export GECKO_OBJDIR=${GECKO_OBJDIR}-opt
fi
if [ "${B2G_DEBUG}" != "0" ]; then
    export GECKO_OBJDIR=${GECKO_OBJDIR}-debug
fi
if [ "${GECKO_PATH/*mozilla-inbound*/mozilla-inbound}" = "mozilla-inbound" ]; then
    export GECKO_OBJDIR=${GECKO_OBJDIR}-m-i
fi
if [ "${GECKO_PATH/*mozilla-central*/mozilla-central}" = "mozilla-central" ]; then
    export GECKO_OBJDIR=${GECKO_OBJDIR}-m-c
fi
if [ "${GECKO_PATH/*b2g-inbound*/b2g-inbound}" = "b2g-inbound" ]; then
    export GECKO_OBJDIR=${GECKO_OBJDIR}-b2g-i
fi
if [ -n "${BRANCH}" ]; then
    export GECKO_OBJDIR=${GECKO_OBJDIR}-${BRANCH}
fi
echo "CC            = ${CC}"
echo "CXX           = ${CXX}"
echo "B2G_DIR       = ${B2G_DIR}"
echo "GECKO         = ${GECKO}"
echo "GECKO_PATH    = ${GECKO_PATH}"
echo "GECKO_OBJDIR  = ${GECKO_OBJDIR}” 
```

```
% export GECKO=../mozilla-central
% ./config.sh nexus-4 (or something else)
% cd gonk-misc
% git remote add posidron https://github.com/posidron/gonk-misc 
% git fetch posidron 
% git checkout faulty
% cd ../
% ./build.sh
% ./flash.sh
```


###Usage Instructions
---

Once you created a build with Faulty support, the following environment variables will be supported:

```
FAULTY_PIPE         randomly close pipes
FAULTY_PICKLE       intercept and exchange values of IPDL method calls
FAULTY_SEED         custom seed value
FAULTY_PROBABILITY  custom probability factor for calling fuzzing functions
FAULTY_CHILDS       fuzz only child processes
FAULTY_PARENT       fuzz only content processes
FAULTY_LARGE_VALUES use large values during the fuzzing
```

A bash script is provided to set these variables and to execute Faulty in a convenient way:

```
./faulty -h         displays the available options.
./faulty -p         runs the B2G process within GDB and tests IPDL method calls 
```

In order to see IPDL method calls, the script also sets the MOZ_IPC_MESSAGE_LOG variable. 




####IPDLs used in Firefox and FirefoxOS
---

```
./content/media/webspeech/synth/ipc/PSpeechSynthesis.ipdl
./content/media/webspeech/synth/ipc/PSpeechSynthesisRequest.ipdl
./dom/bluetooth/ipc/PBluetooth.ipdl
./dom/bluetooth/ipc/PBluetoothRequest.ipdl
./dom/devicestorage/PDeviceStorageRequest.ipdl
./dom/fmradio/ipc/PFMRadio.ipdl
./dom/fmradio/ipc/PFMRadioRequest.ipdl
./dom/indexedDB/ipc/PIndexedDB.ipdl
./dom/indexedDB/ipc/PIndexedDBCursor.ipdl
./dom/indexedDB/ipc/PIndexedDBDatabase.ipdl
./dom/indexedDB/ipc/PIndexedDBDeleteDatabaseRequest.ipdl
./dom/indexedDB/ipc/PIndexedDBIndex.ipdl
./dom/indexedDB/ipc/PIndexedDBObjectStore.ipdl
./dom/indexedDB/ipc/PIndexedDBRequest.ipdl
./dom/indexedDB/ipc/PIndexedDBTransaction.ipdl
./dom/ipc/PBlob.ipdl
./dom/ipc/PBlobStream.ipdl
./dom/ipc/PBrowser.ipdl
./dom/ipc/PContent.ipdl
./dom/ipc/PContentDialog.ipdl
./dom/ipc/PContentPermissionRequest.ipdl
./dom/ipc/PCrashReporter.ipdl
./dom/ipc/PDocumentRenderer.ipdl
./dom/ipc/PMemoryReportRequest.ipdl
./dom/mobilemessage/src/ipc/PMobileMessageCursor.ipdl
./dom/mobilemessage/src/ipc/PSms.ipdl
./dom/mobilemessage/src/ipc/PSmsRequest.ipdl
./dom/network/src/PTCPServerSocket.ipdl
./dom/network/src/PTCPSocket.ipdl
./dom/plugins/ipc/PBrowserStream.ipdl
./dom/plugins/ipc/PPluginBackgroundDestroyer.ipdl
./dom/plugins/ipc/PPluginIdentifier.ipdl
./dom/plugins/ipc/PPluginInstance.ipdl
./dom/plugins/ipc/PPluginModule.ipdl
./dom/plugins/ipc/PPluginScriptableObject.ipdl
./dom/plugins/ipc/PPluginStream.ipdl
./dom/plugins/ipc/PPluginSurface.ipdl
./dom/plugins/ipc/PStreamNotify.ipdl
./dom/src/storage/PStorage.ipdl
./dom/telephony/ipc/PTelephony.ipdl
./dom/telephony/ipc/PTelephonyRequest.ipdl
./gfx/layers/ipc/PCompositable.ipdl
./gfx/layers/ipc/PCompositor.ipdl
./gfx/layers/ipc/PGrallocBuffer.ipdl
./gfx/layers/ipc/PImageBridge.ipdl
./gfx/layers/ipc/PLayer.ipdl
./gfx/layers/ipc/PLayerTransaction.ipdl
./hal/sandbox/PHal.ipdl
./ipc/testshell/PTestShell.ipdl
./ipc/testshell/PTestShellCommand.ipdl
./js/ipc/PJavaScript.ipdl
./layout/ipc/PRenderFrame.ipdl
./netwerk/cookie/PCookieService.ipdl
./netwerk/ipc/PNecko.ipdl
./netwerk/ipc/PRemoteOpenFile.ipdl
./netwerk/ipc/PRtspController.ipdl
./netwerk/protocol/ftp/PFTPChannel.ipdl
./netwerk/protocol/http/PHttpChannel.ipdl
./netwerk/protocol/websocket/PWebSocket.ipdl
./netwerk/protocol/wyciwyg/PWyciwygChannel.ipdl
./uriloader/exthandler/PExternalHelperApp.ipdl
./uriloader/prefetch/POfflineCacheUpdate.ipdl
```

####Registered IPC Messages
---
```
enum IPCMessageStart {  
  PAudioMsgStart,
  PBrowserMsgStart,
  PBrowserStreamMsgStart,
  PCompositorMsgStart,
  PContentDialogMsgStart,
  PContentMsgStart,
  PContentPermissionRequestMsgStart,
  PContextWrapperMsgStart,
  PCookieServiceMsgStart,
  PCrashReporterMsgStart,
  PDeviceStorageRequestMsgStart,
  PDocumentRendererMsgStart,
  PExternalHelperAppMsgStart,
  PFTPChannelMsgStart,
  PGrallocBufferMsgStart,
  PHalMsgStart,
  PHttpChannelMsgStart,
  PImageBridgeMsgStart,
  PImageContainerMsgStart,
  PIndexedDBCursorMsgStart,
  PIndexedDBDatabaseMsgStart,
  PIndexedDBDeleteDatabaseRequestMsgStart,
  PIndexedDBIndexMsgStart,
  PIndexedDBMsgStart,
  PIndexedDBObjectStoreMsgStart,
  PIndexedDBRequestMsgStart,
  PIndexedDBTransactionMsgStart,
  PLayerMsgStart,
  PLayersMsgStart,
  PMemoryReportRequestMsgStart,
  PNeckoMsgStart,
  PObjectWrapperMsgStart,
  POfflineCacheUpdateMsgStart,
  PPluginBackgroundDestroyerMsgStart,
  PPluginIdentifierMsgStart,
  PPluginInstanceMsgStart,
  PPluginModuleMsgStart,
  PPluginScriptableObjectMsgStart,
  PPluginStreamMsgStart,
  PPluginSurfaceMsgStart,
  PRenderFrameMsgStart,
  PSmsMsgStart,
  PStorageMsgStart,
  PStreamNotifyMsgStart,
  PTestShellCommandMsgStart,
  PTestShellMsgStart,
  PWebSocketMsgStart,
  PWyciwygChannelMsgStart,
};

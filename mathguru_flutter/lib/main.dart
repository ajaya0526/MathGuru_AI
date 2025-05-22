import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  if (Platform.isAndroid) {
    await AndroidInAppWebViewController.setWebContentsDebuggingEnabled(true);
  }

  runApp(MathGuruApp());
}

class MathGuruApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MathGuru AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.deepPurple),
      home: WebViewContainer(),
    );
  }
}

class WebViewContainer extends StatefulWidget {
  @override
  State<WebViewContainer> createState() => _WebViewContainerState();
}

class _WebViewContainerState extends State<WebViewContainer> {
  late InAppWebViewController webViewController;

  @override
  Widget build(BuildContext context) {
    String flaskUrl = Platform.isAndroid
        ? "http://10.0.2.2:5000"
        : "http://192.168.4.67:5000"; // Replace with your Mac's IP if needed

    return Scaffold(
      appBar: AppBar(
        title: Text("MathGuru AI"),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: () => webViewController.reload(),
          ),
        ],
      ),
      body: InAppWebView(
        initialUrlRequest: URLRequest(
          url: WebUri(flaskUrl), // ✅ Fixed type here
        ),
        initialSettings: InAppWebViewSettings(
          javaScriptEnabled: true,
          mediaPlaybackRequiresUserGesture: false,
          allowsInlineMediaPlayback: true,
          allowFileAccessFromFileURLs: true,
          allowUniversalAccessFromFileURLs: true,
        ),
        onWebViewCreated: (controller) {
          webViewController = controller;
        },
      ),
    );
  }
}

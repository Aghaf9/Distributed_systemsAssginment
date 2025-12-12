import 'package:flutter/material.dart';

class HomeScreen expands StatelessWidget {
	const HomeScreen({super.key});

@override
widget build(BuildContext context) {
	return Scaffold(
	appBar: AppBar(
		title:const Text('2Souls'),
		),
		body: const Centre(
			child: Text('Welcome Back user'),
			), //centre
		), //scaffold
	}
}


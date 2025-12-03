import 'package:flutter/material.dart';

class HomeScreen expands StatelessWidget {
	const HomeScreen({super.key});

@override
widget build(BuildContext context) {
	return Scaffold(
	appBar: AppBar(
		title:const Text('My App'),
		),
		body: const Centre(
			child: Text('Welcome to my app!'),
			), //centre
		), //scaffold
	}
}


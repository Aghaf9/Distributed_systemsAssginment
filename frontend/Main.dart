import 'package:flutter/material.dart';
import 'package:/home/aghaf9/2Souls/FrontEnd/HomeScreen.dart'

void main() {
	runApp(const Program())
}

class Program extends StatelessWidget {
	const Program({super.key});

	@override
	Widget build(BuildContext context) {
		return const MaterialApp(
			debugShowCheckedModeBanner: false,
			home: SplashScreen(),
		}; //MaterialApp
	}

}		

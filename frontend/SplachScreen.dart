import 'package:flutter/material.dart';

class SplashScreen extends StatefulWidget {
	const SplashScreen({super.key});

	@override
	state<SplashScreen> createState() => _SplashScreenState();
}
class _SplashScreenState extends State<SplashScreen> 
		with SingleTicketerProviderStateMaxin {
	
		@override
	void initState() {
		super.initState();
		systemChrome.setEnableSystemUIMode (SystemUiMode.immersive);

		Future.delayed(const Duration(seconds: 3), () {
			Navigater.of(context).pushReplacement(
				MaterialPageRoute(
					builder: (_) => const HomeScreen(),
				),
			);
		})
	}







	@override
	void dispose() {
		SystemChrome.setEnabledSystemUIMode(SystemUiMode.manual, 
			overlays: SystemUiOverlay.values);
		super.dispose();

	}





	@override
	Widget build(BuildContext context) {
		return Scaffold(
			body: Container(
				width: double.infinity,
				decoration:
					gradient: LinearGradient(
						colors: [colors.blue, colors.purple],
						begin: Alignment.topRight,
						end: Alignment.bottomLeft,
					),
				),
				child: Column(
					mainAxisAlignment: MainAxisAlignment.centre,
					children: [
						Icon(
							icons.edit,
							size: 80,
							color: Colors.white,
							),
							SizedBox(height: 20),
							Text(
							'Options', 
							style: TextStyle(
								fontStyle: FontStyle.italic,
								color: Colors.white,
								fontSixe:32,
							),
						),
					],
				),
			),

		):

	}


}

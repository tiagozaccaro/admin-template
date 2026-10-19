import 'package:flutter/material.dart';

class TenantsScreen extends StatelessWidget {
  const TenantsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Tenants')),
      body: const Center(
        child: Text('Manage tenants, memberships, and invitations'),
      ),
    );
  }
}

# test_schemas.py - Test each schema file individually
try:
    from application.blueprints.customer.customerSchemas import customer_schema
    print("✅ Customer schemas loaded successfully")
except Exception as e:
    print(f"❌ Customer schemas error: {e}")

try:
    from application.blueprints.inventory.inventorySchemas import inventory_schema
    print("✅ Inventory schemas loaded successfully")
except Exception as e:
    print(f"❌ Inventory schemas error: {e}")

try:
    from application.blueprints.mechanic.mechanicSchemas import mechanic_schema
    print("✅ Mechanic schemas loaded successfully")
except Exception as e:
    print(f"❌ Mechanic schemas error: {e}")

try:
    from application.blueprints.service_ticket.serviceTicketSchemas import service_ticket_schema
    print("✅ Service ticket schemas loaded successfully")
except Exception as e:
    print(f"❌ Service ticket schemas error: {e}")
from django.test import TestCase

# Create your tests here.
class OrderCreationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='staff1',
            password='testpass123',
            user_type='staff'
        )
        self.customer = Customer.objects.create(
            name='John Doe',
            phone='1234567890'
        )
        self.shirt = ClothingType.objects.create(
            name='Shirt',
            price=5.00
        )
    
    def test_order_creation(self):
        self.client.login(username='staff1', password='testpass123')
        
        response = self.client.post(reverse('create_order'), {
            'customer': self.customer.id,
            'express_service': False,
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(LaundryOrder.objects.count(), 1)
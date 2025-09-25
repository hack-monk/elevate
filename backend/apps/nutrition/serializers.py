from rest_framework import serializers
from .models import Food, Meal, MealItem


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = [
            'id', 'name', 'brand', 'serving_size', 'calories', 'protein_g',
            'carbs_g', 'fat_g', 'fiber_g', 'sugar_g', 'sodium_mg',
            'is_custom', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_calories(self, value):
        if value < 0:
            raise serializers.ValidationError("Calories cannot be negative")
        return value
    
    def validate_protein_g(self, value):
        if value < 0:
            raise serializers.ValidationError("Protein cannot be negative")
        return value


class MealItemSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source='food.name', read_only=True)
    food_brand = serializers.CharField(source='food.brand', read_only=True)
    
    class Meta:
        model = MealItem
        fields = [
            'id', 'food', 'food_name', 'food_brand', 'quantity',
            'custom_calories', 'custom_protein_g', 'custom_carbs_g', 'custom_fat_g',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class MealSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True, read_only=True)
    total_calories = serializers.SerializerMethodField()
    total_protein_g = serializers.SerializerMethodField()
    total_carbs_g = serializers.SerializerMethodField()
    total_fat_g = serializers.SerializerMethodField()
    
    class Meta:
        model = Meal
        fields = [
            'id', 'date', 'meal_type', 'notes', 'items',
            'total_calories', 'total_protein_g', 'total_carbs_g', 'total_fat_g',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_calories(self, obj):
        total = 0
        for item in obj.items.all():
            if item.custom_calories:
                total += item.custom_calories
            else:
                total += int(item.quantity * item.food.calories)
        return total
    
    def get_total_protein_g(self, obj):
        from decimal import Decimal
        total = Decimal('0')
        for item in obj.items.all():
            if item.custom_protein_g:
                total += item.custom_protein_g
            else:
                total += item.quantity * item.food.protein_g
        return total
    
    def get_total_carbs_g(self, obj):
        from decimal import Decimal
        total = Decimal('0')
        for item in obj.items.all():
            if item.custom_carbs_g:
                total += item.custom_carbs_g
            else:
                total += item.quantity * item.food.carbs_g
        return total
    
    def get_total_fat_g(self, obj):
        from decimal import Decimal
        total = Decimal('0')
        for item in obj.items.all():
            if item.custom_fat_g:
                total += item.custom_fat_g
            else:
                total += item.quantity * item.food.fat_g
        return total


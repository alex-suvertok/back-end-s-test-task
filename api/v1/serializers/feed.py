from rest_framework import serializers


class FeedSummarySerializer(serializers.Serializer):
    feed_id = serializers.IntegerField()
    feed_name = serializers.CharField()
    total = serializers.IntegerField()
    success = serializers.IntegerField()
    error = serializers.IntegerField()
    last_success_at = serializers.DateTimeField(allow_null=True)
    last_error_at = serializers.DateTimeField(allow_null=True)

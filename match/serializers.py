from rest_framework import serializers


class MatchTeamContainerSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()
    touchdown = serializers.IntegerField()
    cas = serializers.IntegerField()
    badly_hurt = serializers.IntegerField()
    serious_injury = serializers.IntegerField()
    kill = serializers.IntegerField()
    extra_fan = serializers.IntegerField()
    fan_factor = serializers.IntegerField()
    gold = serializers.IntegerField()

from rest_framework.throttling import SimpleRateThrottle


class SurveySubmitRateThrottle(SimpleRateThrottle):
    scope = 'survey_submit'

    def get_cache_key(self, request, view):
        if request.method != 'POST':
            return None
        ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}

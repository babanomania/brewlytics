{% macro postgres__truncate_relation(relation) -%}
  {% call statement('truncate_relation') -%}
    truncate table {{ relation }} cascade
  {%- endcall %}
{% endmacro %}
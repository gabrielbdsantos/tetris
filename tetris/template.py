# coding = utf-8

BLOCKMESHDICT_TEMPLATE = """// Generated using Tetris v{{ version }}
{%- if header %}
{{ header }}{% endif %}
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

scale {{ scale }};
fastMerge yes;

{% if geometries -%}
geometry
{
    {%- for g in geometries %}
    {{ g.write() }}{% endfor %}
}

{% endif -%}
vertices
(
    {%- for v in vertices %}
    {{ v.write() }}{% endfor %}
);

blocks
(
    {%- for b in blocks %}
    {{ b.write() }}{% endfor %}
);

{% if edges -%}
edges
(
    {%- for e in edges %}
    {{ e.write() }}{% endfor %}
);

{% endif -%}
{% if faces -%}
faces
(
    {%- for e in faces %}
    {{ e.write() }}{% endfor %}
);

{% endif -%}
{%- if defaultPatch %}
{{- defaultPatch.write() }}

{% endif -%}
{% if boundary -%}
boundary
(
    {%- for b in boundaries %}
    {{ b.write() }}{% endfor %}
);

{% endif -%}
{% if patches -%}
patches
(
    {%- for p in patches %}
    {{ p.write() }}{% endfor %}
);

{% endif -%}
{% if mergePatchPairs -%}
mergePatchPairs
(
    {%- for m in mergePatchPairs %}
    {{ m.write() }}{% endfor %}
);

{% endif -%}
// ************************************************************************* //
{%- if footer %}
{{ footer }}{% endif %}
"""

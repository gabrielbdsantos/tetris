# coding = utf-8

BLOCKMESHDICT_TEMPLATE = """// Automatically generated by Tetris v{{ version }}
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

edges
(
    {%- for e in edges %}
    {{ e.write() }}{% endfor %}
);

faces
(
    {%- for e in faces %}
    {{ e.write() }}{% endfor %}
);

defaultPatch
(
    {%- if defaultPatch %}
    {{- defaultPatch.write() }}{% endif %}
);

boundary
(
    {%- for b in boundaries %}
    {{ b.write() }}{% endfor %}
);

patches
(
    {%- for p in patches %}
    {{ p.write() }}{% endfor %}
);

mergePatchPairs
(
    {%- for m in mergePatchPairs %}
    {{ m.write() }}{% endfor %}
);

// ************************************************************************* //
{%- if footer %}
{{ footer }}{% endif %}
"""

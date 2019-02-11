{% macro insert_lines(comment, lines) %}
	//// {{comment}} ////
	{% for line in lines %}
	{{line}}
	{% endfor %}
{% endmacro %}

{% macro insert_lines_commented(comment, lines) %}
	// {{comment}}
	{% for line in lines %}
	//{{line}}
	{% endfor %}
{% endmacro %}

{% macro insert_support_code_lines_commented() %}
	{{ insert_lines_commented('SUPPORT CODE', support_code_lines) }}
{% endmacro %}

{% macro insert_denormals_code_lines() %}
	{{ insert_lines('HANDLE DENORMALS', denormals_code_lines) }}
{% endmacro %}

{% macro insert_hashdefine_lines() %}
	{{ insert_lines('HASH DEFINES', hashdefine_lines) }}
{% endmacro %}

{% macro insert_pointers_lines() %}
	{{ insert_lines('POINTERS', pointers_lines) }}
{% endmacro %}

{% macro insert_vector_code() %}
	{{ insert_lines('MAIN CODE LINES', vector_code) }}
{% endmacro %}

{% macro insert_group_preamble() %}
	{{ insert_support_code_lines_commented() }}
	{{ insert_denormals_code_lines() }}
	{{ insert_hashdefine_lines() }}
	{{ insert_pointers_lines() }}
{% endmacro %}

{% macro support_code() %}
#define _INDEX(_neuron, _compartment) ((_neuron)*_n_compartments + (_compartment))
#define _INDEX_SEC(_neuron, _section) ((_neuron)*_n_sections + (_section))
#define _INDEX_SEC1(_neuron, _section) ((_neuron)*(_n_sections+1) + (_section))
#define _INDEX_CHILDREN(_neuron, _child) ((_neuron)*_max_children + (_child))
	{{support_code_lines|autoindent}}
{% endmacro %}

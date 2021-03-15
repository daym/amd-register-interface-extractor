#include <assert.h>
#include <glib.h>
#include <gtk/gtk.h>
#include <libxml/tree.h>
#include <libxml/xpath.h>

#define C_TYPE 0
#define C_NAME 1
#define C_TOOLTIP 2

static xmlDocPtr input_document;
static xmlXPathContextPtr input_xpath_context;
static GtkTreeStore* store;
static GtkTreeView* tree_view;

static const char* device_keys[] = {"name", "version", "addressUnitBits", "width", "size", "resetValue", "resetMask", "vendor", "vendorID", "series", "licenseText", "access", "description", NULL};
static const char* peripheral_keys[] = {"name", "version", "size", "groupName", "baseAddress", "addressBlock", "resetValue", "resetMask", "access", "modifiedWriteValues", "description", NULL};
static const char* register_keys[] = {"name", "displayName", "addressOffset", "size", "access", "resetValue", "resetMask", "alternativeRegister", "description", NULL};
static const char* cluster_keys[] = {"name", "addressOffset", "size", "access", "resetValue", "resetMask", "alternateCluster", "description", NULL};
static const char* field_keys[] = {"name", "bitOffset", "bitWidth", "access", "bitRange", "msb", "lsb", "description", NULL};
static const char* interrupt_keys[] = {"name", "value", "description", NULL};

static const char** keys_of_element_type(const char* type) {
	if (strcmp(type, "cluster") == 0) {
		return cluster_keys;
	} else if (strcmp(type, "device") == 0) {
		return device_keys;
	} else if (strcmp(type, "peripheral") == 0) {
		return peripheral_keys;
	} else if (strcmp(type, "register") == 0) {
		return register_keys;
	} else if (strcmp(type, "cluster") == 0) {
		return cluster_keys;
	} else if (strcmp(type, "field") == 0) {
		return field_keys;
	} else if (strcmp(type, "interrupt") == 0) {
		return interrupt_keys;
	} else {
		return NULL;
	}
}

static int pseudo_attribute_P(const char* type, const char* name) {
	const char** keys = keys_of_element_type(type);
	if (keys) {
		int i;
		for (i = 0; keys[i]; ++i) {
			if (strcmp(keys[i], name) == 0)
				return TRUE;
		}
		return FALSE;
	} else
		return FALSE;
}

static const char* child_element_text(xmlNodePtr root, const char* key) {
	xmlNodePtr child;
	for (child = root->children; child; child = child->next) {
		if (child->type == XML_ELEMENT_NODE && strcmp(key, child->name) == 0) {
			return xmlNodeListGetString(input_document, child->children, 1);
		}
	}
	return NULL;
}

static void resolve_derivedFrom(xmlNodePtr root) {
	// If ROOT has a 'derivedFrom' attribute, find an element with that name and copy all its children--except for the ones ROOT already has
	xmlChar* derivedFrom = xmlGetProp(root, "derivedFrom");
	if (derivedFrom) {
		xmlNodePtr sibling = NULL;
		for (sibling = xmlPreviousElementSibling(root); sibling; sibling = xmlPreviousElementSibling(sibling)) {
			if (sibling->type == XML_ELEMENT_NODE && strcmp(sibling->name, root->name) == 0) {
				const char* name = child_element_text(sibling, "name");
				if (name && strcmp(name, derivedFrom) == 0) {
					xmlFree(name);
					break;
				}
				xmlFree(name);
			}
		}
		if (!sibling) { /* didn't find the node in the siblings--try some more aggressive means */
#if 0
			char* xpath_expression = g_strdup_printf("//register[name='%s']", derivedFrom); // XXX: injection
			xmlXPathObjectPtr result = xmlXPathEvalExpression(xpath_expression, input_xpath_context);
			if (!xmlXPathNodeSetIsEmpty(result->nodesetval)) {
				sibling = result->nodesetval->nodeTab[0];
			}
			xmlXPathFreeObject(result);
#endif
		}
		if (sibling) {
			resolve_derivedFrom(sibling);
			xmlNodePtr child;
			for(child = sibling->children; child; child = child->next) { // weird-ass attributes
				if (child->type == XML_ELEMENT_NODE) {
					const char* key = xmlNodeListGetString(input_document, child->children, 1);
					if (key && child_element_text(root, key) == NULL) { // default this one to sibling's item
						xmlNodePtr xchild = xmlCopyNode(child, 1);
						xmlAddChild(root, xchild);
					}
				}
			}
		}
	}
}

static char* calculate_tooltip(const char* type, xmlNodePtr root) {
	const char* result = "";
	int i;
	const char** keys = keys_of_element_type(type);
	if (keys) {
		for (i = 0; i < keys[i]; ++i) {
			const char* value = child_element_text(root, keys[i]);
			if (value)
				result = g_strdup_printf("%s\n%s: %s", result, keys[i], value);
		}
	}
	result = g_strdup_printf("%s\n%s", result, g_strstrip(xmlNodeListGetString(input_document, root->children, 1)));
	if (result[0])
		return &result[1];
	else
		return result;
}

static void traverse(xmlNodePtr root, GtkTreeIter* store_parent) {
	xmlNodePtr child;
	const char* type = (root->type == XML_ELEMENT_NODE) ? root->name : NULL;
	if (root->type == XML_ELEMENT_NODE)
		resolve_derivedFrom(root);
	if (type == NULL)
		type = "?";
	const char* name = child_element_text(root, "name");
	if (name == NULL || !name[0])
		name = type;
	else
		name = g_strdup_printf("%s %s", type, name);
	const char* tooltip = calculate_tooltip(type, root);
	GtkTreeIter iter;
	gtk_tree_store_append(store, &iter, store_parent);
	if (strcmp(type, "registers") == 0)
	    gtk_tree_view_expand_to_path(tree_view, gtk_tree_model_get_path(store, &iter));
	tooltip = g_markup_escape_text(tooltip, -1);
	gtk_tree_store_set(store, &iter, C_TYPE, type, C_NAME, name, C_TOOLTIP, tooltip, -1);
	for (child = root->children; child; child = child->next) {
		if (child->type == XML_ELEMENT_NODE && pseudo_attribute_P(type, child->name)) {
			//g_warning("ignore %s", child->name);
		} else if (child->type == XML_ELEMENT_NODE) {
			traverse(child, &iter);
		}
	}
}

int main(int argc, char* argv[]) {
	gtk_init(&argc, &argv);
	if (!argv[1]) {
		g_error("input file missing");
		exit(1);
	} else {
		input_document = xmlParseFile(argv[1]);
		if (input_document == NULL) {
			g_error("could not open input file \"%s\"", argv[1]);
			exit(1);
		}
		input_xpath_context = xmlXPathNewContext(input_document);
		if (input_xpath_context == NULL) {
			g_error("could not create xpath context");
			exit(1);
		}
	}
	store = gtk_tree_store_new(3, G_TYPE_STRING, G_TYPE_STRING, G_TYPE_STRING);

	GtkScrolledWindow* scrolled_window = gtk_scrolled_window_new(NULL, NULL);
	gtk_scrolled_window_set_policy(scrolled_window, GTK_POLICY_NEVER, GTK_POLICY_AUTOMATIC);
	GtkTreeViewColumn* col0 = gtk_tree_view_column_new_with_attributes("Name", gtk_cell_renderer_text_new(), "text", C_NAME, NULL);
	tree_view = gtk_tree_view_new();
	gtk_tree_view_set_model(tree_view, store);
	gtk_tree_view_set_tooltip_column(tree_view, C_TOOLTIP);
	gtk_tree_view_set_headers_visible(tree_view, FALSE);
	gtk_tree_view_set_search_column(tree_view, C_NAME);
	gtk_tree_view_append_column(tree_view, col0);
	gtk_container_add(scrolled_window, tree_view);

	GtkWindow* window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
	// TODO: realpath for first one
	gtk_window_set_title(window, g_strdup_printf("%s - %s", argv[1], argv[0]));
	g_signal_connect(window, "destroy", gtk_main_quit, NULL);
	gtk_container_add(window, scrolled_window);
	gtk_widget_show_all(window);

	traverse(xmlDocGetRootElement(input_document), NULL);

	gtk_main();
	return 0;
}

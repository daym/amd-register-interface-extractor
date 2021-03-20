#include <assert.h>
#include <glib.h>
#include <gtk/gtk.h>
#include <stdint.h>
#include <stdlib.h>
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
static const char* register_keys[] = {"name", "displayName", "alternateRegister", "addressOffset", "size", "dim", "dimIncrement", "dimIndex", "dimName", "dimArrayIndex", "access", "resetValue", "resetMask", "alternativeRegister", "description", NULL};
static const char* cluster_keys[] = {"name", "addressOffset", "size", "dim", "dimIncrement", "dimIndex", "dimName", "dimArrayIndex", "access", "resetValue", "resetMask", "alternateCluster", "description", NULL};
static const char* field_keys[] = {"name", "bitOffset", "bitWidth", "access", "bitRange", "msb", "lsb", "description", NULL};
static const char* interrupt_keys[] = {"name", "value", "description", NULL};
static const char* no_keys[] = { NULL };

/* Returns a null-terminated list of keys that are supposed to be SVD attributes rather than child nodes.
   @param type The SVD type of node (an xml element tag name)
 */
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
		return no_keys;
	}
}

/* Returns whether the given xml node (given the SVD type of node and the name of the element to be checked) is an attribute or not.
   @param type The SVD type of node (an xml element tag name)
   @param name The tag name of the element to be checked.
   @return Whether the element is an attribute of the SVD node
 */
static int pseudo_attribute_P(const char* type, const char* name) {
	const char** keys = keys_of_element_type(type);
	int i;
	for (i = 0; keys[i]; ++i) {
		if (strcmp(keys[i], name) == 0)
			return TRUE;
	}
	return FALSE;
}

/* Retrieves the (first) element that is a child of ROOT and has the tag name KEY.  (This is how pseudo attributes are stored in SVD)
   @param root The XML element whose children are to be checked
   @param key The child element of ROOT that is to be searched for, by tag name
   @return A newly allocated string containing the text body of the child element so found, or NULL if it was not found.  Caller should free using xmlFree.
 */
static xmlChar* child_element_text(xmlNodePtr root, const char* key) {
	xmlNodePtr child;
	for (child = root->children; child; child = child->next) {
		if (child->type == XML_ELEMENT_NODE && strcmp(key, child->name) == 0) {
			return xmlNodeListGetString(input_document, child->children, 1);
		}
	}
	return NULL;
}

/* If ROOT has a 'derivedFrom' attribute, find an element with that name and copy all its children--except for the ones ROOT already has.
   This implements the SVD inheritance functionality.
   @param root The node that is to be checked for the 'derivedFrom' attribute (and whose children are to be mutated)
   Side effect: Mutates ROOT.
 */
static void resolve_derivedFrom(xmlNodePtr root) {
	xmlChar* derivedFrom = xmlGetProp(root, "derivedFrom");
	if (derivedFrom) {
		xmlNodePtr sibling = NULL;
		// Find sibling with name equal to derivedFrom
		for (sibling = xmlPreviousElementSibling(root); sibling; sibling = xmlPreviousElementSibling(sibling)) {
			if (sibling->type == XML_ELEMENT_NODE && strcmp(sibling->name, root->name) == 0) {
				xmlChar* name = child_element_text(sibling, "name");
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
		if (sibling) { // If the sibling to be derived from has been found
			resolve_derivedFrom(sibling);
			xmlNodePtr child;
			// Copy all the pseudo attributes over that we don't already have
			for(child = sibling->children; child; child = child->next) {
				if (child->type == XML_ELEMENT_NODE) {
					const char* child_key = child->name;
					xmlChar* our_value = child_element_text(root, child_key);
					if (our_value == NULL) {
						xmlNodePtr xchild = xmlCopyNode(child, 1);
						xmlAddChild(root, xchild);
					} else
						xmlFree(our_value);
				}
			}
		}
	}
}

/* Evaluates SVD integer numeral and returns the number it represents. */
static uint64_t eval_int(const char* address_string) {
	if (address_string[0] == '0' && address_string[1] == 'x') {
		return strtoull(&address_string[2], NULL, 16);
	} else {
		return strtoull(address_string, NULL, 10);
	}
}

/* Given a SVD node (given by type and root), calculates tooltip text for it.
   @param type The type of ROOT
   @param root The node whose information to show in the tooltip
   @param base_address The base address for addressOffsets in ROOT.
   @return The tooltip text
 */
static char* calculate_tooltip(const char* type, xmlNodePtr root, uint64_t base_address) {
	char* result = g_strdup("");
	int i;
	const char** keys = keys_of_element_type(type);
	{
		xmlChar* addressOffset = child_element_text(root, "addressOffset") ?: child_element_text(root, "baseAddress");
		if (addressOffset) {
			uint64_t address_offset = eval_int(addressOffset);
			result = g_strdup_printf("\n(absolute address: 0x%X)", base_address + address_offset);
			xmlFree(addressOffset);
		}
	}
	for (i = 0; keys[i]; ++i) {
		xmlChar* value = child_element_text(root, keys[i]);
		if (value) {
			result = g_strdup_printf("%s\n%s: %s", result, keys[i], value);
			xmlFree(value);
		}
	}
	{
		char *text = xmlNodeListGetString(input_document, root->children, 1);
		if (text) {
			result = g_strdup_printf("%s\n%s", result, text ? g_strstrip(text) : "");
			xmlFree(text);
		}
	}
	return result;
}

/** Stores ROOT under STORE_PARENT, uses base_address as base address for all the calculations under it.
    @param root source (xml node)
    @param store_parent destination (in a GtkTreeStore)
    @param base_address base address to use for calculations
 */
static void traverse(xmlNodePtr root, GtkTreeIter* store_parent, uint64_t base_address) {
	xmlNodePtr child;
	const char* type = (root->type == XML_ELEMENT_NODE) ? root->name : "?";
	if (root->type == XML_ELEMENT_NODE)
		resolve_derivedFrom(root);
	char* name;
	{
		xmlChar* xml_name = child_element_text(root, "name");
		if (xml_name == NULL || !xml_name[0])
			name = g_strdup(type);
		else
			name = g_strdup_printf("%s %s", type, xml_name);
		if (xml_name)
			xmlFree(xml_name);
	}
	char* tooltip = calculate_tooltip(type, root, base_address);
	{
		xmlChar* baseAddress = child_element_text(root, "addressOffset") ?: child_element_text(root, "baseAddress");
		if (baseAddress) {
			base_address += eval_int(baseAddress);
			xmlFree(baseAddress);
		}
	}

	GtkTreeIter iter;
	gtk_tree_store_append(store, &iter, store_parent);
	if (strcmp(type, "registers") == 0) {
		gtk_tree_view_expand_to_path(tree_view, gtk_tree_model_get_path(GTK_TREE_MODEL(store), &iter));
	}
	{
		char* x_tooltip = g_markup_escape_text(tooltip, -1);
		if (x_tooltip) {
			g_free(tooltip);
			tooltip = x_tooltip;
		}
	}
	gtk_tree_store_set(store, &iter, C_TYPE, type, C_NAME, name, C_TOOLTIP, tooltip, -1);
	g_free(tooltip);
	g_free(name);
	for (child = root->children; child; child = child->next) {
		if (child->type == XML_ELEMENT_NODE && pseudo_attribute_P(type, child->name)) {
			//g_warning("ignore %s", child->name);
		} else if (child->type == XML_ELEMENT_NODE) {
			traverse(child, &iter, base_address);
		}
	}
}

int main(int argc, char* argv[]) {
	gtk_init(&argc, &argv);
	if (argc < 2 || !argv[0] || !argv[1]) {
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

	GtkScrolledWindow* scrolled_window = GTK_SCROLLED_WINDOW(gtk_scrolled_window_new(NULL, NULL));
	gtk_scrolled_window_set_policy(scrolled_window, GTK_POLICY_NEVER, GTK_POLICY_AUTOMATIC);
	GtkTreeViewColumn* col0 = gtk_tree_view_column_new_with_attributes("Name", gtk_cell_renderer_text_new(), "text", C_NAME, NULL);
	tree_view = GTK_TREE_VIEW(gtk_tree_view_new());
	gtk_tree_view_set_model(tree_view, GTK_TREE_MODEL(store));
	gtk_tree_view_set_tooltip_column(tree_view, C_TOOLTIP);
	gtk_tree_view_set_headers_visible(tree_view, FALSE);
	gtk_tree_view_set_search_column(tree_view, C_NAME);
	gtk_tree_view_append_column(tree_view, col0);
	gtk_container_add(GTK_CONTAINER(scrolled_window), GTK_WIDGET(tree_view));

	GtkWindow* window = GTK_WINDOW(gtk_window_new(GTK_WINDOW_TOPLEVEL));
	// TODO: realpath for first one
	gtk_window_set_title(window, g_strdup_printf("%s - %s", argv[1], argv[0]));
	g_signal_connect(window, "destroy", gtk_main_quit, NULL);
	gtk_container_add(GTK_CONTAINER(window), GTK_WIDGET(scrolled_window));
	gtk_window_set_default_size(window, 400, 400);
	gtk_widget_show_all(GTK_WIDGET(window));

	traverse(xmlDocGetRootElement(input_document), NULL, 0);

	gtk_main();
	return 0;
}

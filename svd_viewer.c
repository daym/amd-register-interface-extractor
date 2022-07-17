#include <assert.h>
#include <glib.h>
#include <gtk/gtk.h>
#include <stdint.h>
#include <stdlib.h>
#include <libxml/tree.h>

#define C_TYPE 0
#define C_NAME 1
#define C_TOOLTIP 2

static xmlDocPtr input_document;
static GtkTreeStore* store;
static GtkTreeView* tree_view;

static const char* device_keys[] = {"name", "version", "addressUnitBits", "width", "size", "resetValue", "resetMask", "vendor", "vendorID", "series", "licenseText", "access", "description", NULL};
static const char* peripheral_keys[] = {"name", "version", "size", "groupName", "baseAddress", "addressBlock", "resetValue", "resetMask", "access", "modifiedWriteValues", "description", NULL};
static const char* register_keys[] = {"name", "displayName", "alternateRegister", "addressOffset", "size", "dim", "dimIncrement", "dimIndex", "dimName", "dimArrayIndex", "access", "resetValue", "resetMask", "alternativeRegister", "description", NULL};
static const char* cluster_keys[] = {"name", "addressOffset", "size", "dim", "dimIncrement", "dimIndex", "dimName", "dimArrayIndex", "access", "resetValue", "resetMask", "alternateCluster", "description", NULL};
static const char* field_keys[] = {"name", "bitOffset", "bitWidth", "access", "bitRange", "msb", "lsb", "description", "modifiedWriteValues", NULL};
static const char* interrupt_keys[] = {"name", "value", "description", NULL};
static const char* enumeratedValue_keys[] = {"name", "value", "description", "isDefault", NULL};
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
	} else if (strcmp(type, "enumeratedValue") == 0) {
		return enumeratedValue_keys;
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

// TODO: Similar for <field> (PERIPHERAL.REGISTER.FIELD), <cluster> (PERIPHERAL.CLUSTER)

static GHashTable* register_by_name; /* contains a map from PERIPHERAL.REGISTER to xml node of the register */
static GHashTable* peripheral_by_name; /* contains a map from peripheral name to xml node of the peripheral */

/* If ROOT has a 'derivedFrom' attribute, find an element with that name and copy all its children--except for the ones ROOT already has.
   This implements the SVD inheritance functionality.
   @param root The node that is to be checked for the 'derivedFrom' attribute (and whose children are to be mutated)
   @param PERIPHERAL_NAME The peripheral the element WITH the derivedFrom attribute is in.
   Side effect: Mutates ROOT.
 */
static void resolve_derivedFrom(xmlNodePtr root, const char* peripheral_name) {
	xmlChar* derivedFrom = xmlGetProp(root, "derivedFrom");
	if (derivedFrom) {
		const char* type = (root->type == XML_ELEMENT_NODE) ? root->name : "?";
		int reg = strcmp(type, "register") == 0;
		int peripheral = strcmp(type, "peripheral") == 0;
		xmlNodePtr reference = NULL;
		const char* fq_derivedFrom = derivedFrom;
		const char* reference_peripheral_name = peripheral_name;
		if (reg) {
			xmlChar* q = strchr(derivedFrom, '.');
			if (q) { // FQ
				fq_derivedFrom = g_strdup(derivedFrom);
				*q = 0;
				reference_peripheral_name = derivedFrom;
			} else {
				fq_derivedFrom = g_strdup_printf("%s.%s", peripheral_name, derivedFrom);
			}
			reference  = g_hash_table_lookup(register_by_name, fq_derivedFrom);
		} else if (peripheral) {
			reference  = g_hash_table_lookup(peripheral_by_name, derivedFrom);
		}
		if (reference) { // If the reference to be derived from has been found
			if (root == reference) { /* shitty trivial cycle detector */
				xmlChar* xml_name = child_element_text(root, "name");
				fprintf(stderr, "Warning: Ignoring cycle between %s.%s and %s.%s\n", peripheral_name, xml_name, peripheral_name, xml_name);
			} else {
				resolve_derivedFrom(reference, reference_peripheral_name);
			}
			xmlNodePtr child;
			// Copy all the pseudo attributes over that we don't already have
			for(child = reference->children; child; child = child->next) {
				if (child->type == XML_ELEMENT_NODE) {
					// Note: Here, we should also recursively call derivedFrom (for all the children of CHILD, too).
					// Note: What's more, if that one isn't an absolute reference, it has to be completed by adding the OLD peripheral reference.
					const char* child_key = child->name;
					xmlChar* our_value = child_element_text(root, child_key);
					if (our_value == NULL) {
						xmlNodePtr xchild = xmlCopyNode(child, 1);
						xmlAddChild(root, xchild);
					} else
						xmlFree(our_value);
				}
			}
		} else {
			g_warning("Could not find %s referenced: '%s'", reg ? "register" : peripheral ? "peripheral" : "element", derivedFrom);
		}
		xmlFree(derivedFrom);
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
	GString* result;
	int i;
	result = g_string_new(NULL);
	const char** keys = keys_of_element_type(type);
	{
		xmlChar* addressOffset = child_element_text(root, "addressOffset") ?: child_element_text(root, "baseAddress");
		if (addressOffset) {
			uint64_t address_offset = eval_int(addressOffset);
			g_string_append_printf(result, "\n(absolute address: 0x%X)", base_address + address_offset);
			xmlFree(addressOffset);
		}
	}
	for (i = 0; keys[i]; ++i) {
		if (strcmp(keys[i], "addressBlock") == 0) {
			char* value = g_strdup_printf("");
			xmlNodePtr q = NULL;
			for (q = root->children; q; q = q->next) {
				if (q->type == XML_ELEMENT_NODE && strcmp(q->name, keys[i]) == 0) {
					for (xmlNodePtr child = q->children; child; child = child->next) {
						if (child->type == XML_ELEMENT_NODE) {
							value = g_strdup_printf("%s%s: %s, ", value, child->name, xmlNodeListGetString(input_document, child->children, 1));
						}
					}
					value = g_strdup_printf("%s\n", value);
				}
			}
			g_string_append_printf(result, "\n%s: %s", keys[i], value);
			continue;
		} else {
			xmlChar* value = child_element_text(root, keys[i]);
			if (value) {
				g_string_append_printf(result, "\n%s: %s", keys[i], value);
				xmlFree(value);
			}
		}
	}
	{
		xmlChar *text = xmlNodeListGetString(input_document, root->children, 1);
		if (text) {
			g_string_append_printf(result, "\n%s", text ? g_strstrip(text) : "");
			xmlFree(text);
		}
	}
	return g_string_free(result, FALSE);
}

/** Registers all registers in register_by_name.
    Side effects: Fills global variable register_by_name.
  */
static void register_elements(xmlNodePtr root, const char* peripheral_name) {
	xmlNodePtr child;
	const char* type = (root->type == XML_ELEMENT_NODE) ? root->name : "?";
	int reg = strcmp(type, "register") == 0;
	int peripheral = strcmp(type, "peripheral") == 0;
	if (root->type == XML_ELEMENT_NODE && (reg || peripheral)) {
		xmlChar* xml_name = child_element_text(root, "name");
		if (peripheral) {
			assert(xml_name);
			peripheral_name = xml_name ? xml_name : "?";
		}
		if (xml_name) {
			if (peripheral) {
				g_hash_table_insert(peripheral_by_name, xml_name, root);
			} else if (reg) {
				char* q = g_strdup_printf("%s.%s", peripheral_name, xml_name);
				g_hash_table_insert(register_by_name, q, root);
				//g_free(q);
			}
		}
	}
	for (child = root->children; child; child = child->next) {
		if (child->type == XML_ELEMENT_NODE && pseudo_attribute_P(type, child->name)) {
			//g_warning("ignore %s", child->name);
		} else if (child->type == XML_ELEMENT_NODE) {
			register_elements(child, peripheral_name);
		}
	}
}

/** Stores ROOT under STORE_PARENT, uses base_address as base address for all the calculations under it.
    Precondition: Expects register_by_name to be available already.
    @param root source (xml node)
    @param store_parent destination (in a GtkTreeStore)
    @param base_address base address to use for calculations
 */
static void traverse(xmlNodePtr root, GtkTreeIter* store_parent, uint64_t base_address, const char* peripheral_name) {
	xmlNodePtr child;
	const char* type = (root->type == XML_ELEMENT_NODE) ? root->name : "?";
	if (root->type == XML_ELEMENT_NODE)
		resolve_derivedFrom(root, peripheral_name);
	char* name;
	{
		xmlChar* xml_name = child_element_text(root, "name");
		if (xml_name == NULL || !xml_name[0])
			name = g_strdup(type);
		else
			name = g_strdup_printf("%s (a %s)", xml_name, type);
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
		GtkTreePath* tree_path = gtk_tree_model_get_path(GTK_TREE_MODEL(store), &iter);
		gtk_tree_view_expand_to_path(tree_view, tree_path);
		gtk_tree_path_free(tree_path);
	}
	{
		char* x_tooltip = g_markup_escape_text(g_strchug(tooltip), -1);
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
			int peripheral = strcmp(child->name, "peripheral") == 0;
			xmlChar* xml_name = child_element_text(child, "name");
			if (peripheral) {
				peripheral_name = xml_name ? xml_name : "?";
			}
			traverse(child, &iter, base_address, peripheral_name);
		}
	}
}

static void go_up_cb(GtkButton* button, GtkTreeView* tree_view) {
	GtkTreePath* path = NULL;
	gtk_tree_view_get_cursor(tree_view, &path, NULL);
	if (gtk_tree_path_up(path)) {
		gtk_tree_view_set_cursor(tree_view, path, NULL, FALSE);
	}
}

static void expand_all_cb(GtkButton* button, GtkTreeView* tree_view) {
	gtk_tree_view_expand_all(tree_view);
}

static void collapse_all_cb(GtkButton* button, GtkTreeView* tree_view) {
	gtk_tree_view_collapse_all(tree_view);
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

	GtkButton* go_up_button = GTK_BUTTON(gtk_button_new_with_label("Go up"));
	g_signal_connect(G_OBJECT(go_up_button), "clicked", G_CALLBACK(go_up_cb), tree_view);

	GtkButton* expand_all_button = GTK_BUTTON(gtk_button_new_with_label("Expand all"));
	g_signal_connect(G_OBJECT(expand_all_button), "clicked", G_CALLBACK(expand_all_cb), tree_view);

	GtkButton* collapse_all_button = GTK_BUTTON(gtk_button_new_with_label("Collapse all"));
	g_signal_connect(G_OBJECT(collapse_all_button), "clicked", G_CALLBACK(collapse_all_cb), tree_view);

	GtkButtonBox* buttons = GTK_BUTTON_BOX(gtk_button_box_new(GTK_ORIENTATION_VERTICAL));
	gtk_box_pack_start(GTK_BOX(buttons), GTK_WIDGET(go_up_button), FALSE, FALSE, 7);
	gtk_box_pack_start(GTK_BOX(buttons), GTK_WIDGET(expand_all_button), FALSE, FALSE, 7);
	gtk_box_pack_start(GTK_BOX(buttons), GTK_WIDGET(collapse_all_button), FALSE, FALSE, 7);

	GtkBox* box = GTK_BOX(gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 7));
	gtk_box_pack_start(GTK_BOX(box), GTK_WIDGET(scrolled_window), TRUE, TRUE, 0);
	gtk_box_pack_start(GTK_BOX(box), GTK_WIDGET(buttons), FALSE, TRUE, 0);

	GtkWindow* window = GTK_WINDOW(gtk_window_new(GTK_WINDOW_TOPLEVEL));
	// TODO: realpath for first one
	gtk_window_set_title(window, g_strdup_printf("%s - %s", argv[1], argv[0]));
	g_signal_connect(window, "destroy", gtk_main_quit, NULL);
	gtk_container_add(GTK_CONTAINER(window), GTK_WIDGET(box));
	gtk_window_set_default_size(window, 400, 400);
	gtk_widget_show_all(GTK_WIDGET(window));

	register_by_name = g_hash_table_new(g_str_hash, g_str_equal);
	peripheral_by_name = g_hash_table_new(g_str_hash, g_str_equal);
	register_elements(xmlDocGetRootElement(input_document), "");
	traverse(xmlDocGetRootElement(input_document), NULL, 0, "");

	gtk_main();
	return 0;
}
